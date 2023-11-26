import asyncio
import time
import uuid
from functools import partial
from os.path import exists
from threading import Lock

from PyQt5 import QtCore, QtWidgets

from gui.widgets.LoginForm import LoginForm
from gui.widgets.ShowErrorDialog import ShowErrorDialog
from model.Event import Event
from model.UploadQueueMedia import UploadQueueMedia
from service.EventService import EventService
from service.MailService import MailService
from service.QueueMediaService import QueueMediaService
from service.LocalizationService import *
from model.Hosting import Hosting
from gui.widgets.LoadingButton import AnimatedButton
from gui.widgets.AddUploadQueueByDirectoryForm import AddUploadQueueByDirectoryForm
import kthread
from PyQt5.QtCore import QTimer
from service.LoggingService import *
import traceback
from datetime import datetime
import os, glob

from service.videohosting_service.exception.NeedCreateSomeActionOnVideohostingException import \
    NeedCreateSomeActionOnVideohostingException
from service.videohosting_service.exception.VideoInTooLowResolutionException import VideoInTooLowResolutionException


class UploadQueuePageWidget(QtWidgets.QTableWidget):
    state_service = StateService()
    event_service = EventService()
    queue_media_service = QueueMediaService()
    queue_media_list = state_service.get_upload_queue_media()
    settings = state_service.get_settings()
    upload_thread_dict = {}
    lock_bool = False

    def __init__(self, central_widget):
        super().__init__(central_widget)
        self.lock = Lock()
        self.setMinimumSize(QtCore.QSize(0, 440))
        self.setObjectName("upload_queue_page_widget")
        self.setColumnCount(6)
        self.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(5, item)

        self.horizontalHeader().setDefaultSectionSize(155)
        horizontal_layout = QtWidgets.QHBoxLayout(self)
        horizontal_layout.setObjectName("horizontal_layout")

        self.add_button = AnimatedButton(central_widget)
        self.add_button.setObjectName("add_button")
        self.add_button.setText(get_str('add_upload_files_by_dir'))
        horizontal_layout.addWidget(self.add_button)
        horizontal_layout.setAlignment(QtCore.Qt.AlignBottom)

        self.add_button.clicked.connect(self.on_add)

        item = self.horizontalHeaderItem(0)
        item.setText(get_str('video'))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str('upload_target'))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str('videohosting'))
        item = self.horizontalHeaderItem(3)
        item.setText(get_str('status'))
        item = self.horizontalHeaderItem(4)
        item.setText(get_str('action'))
        item = self.horizontalHeaderItem(5)
        item.setText(get_str('delete'))

        for queue_media in self.queue_media_list:
            self.insert_queue_media(queue_media)

        self.updating_upload_items = QTimer(self)
        self.updating_upload_items.timeout.connect(self.update_upload_items)
        self.updating_upload_items.start(10_000)

        self.updating_media_timer = QTimer(self)
        self.updating_media_timer.timeout.connect(self.update_queue_media)
        self.updating_media_timer.start(10_000)

        self.uploading_by_schedule_timer = QTimer(self)
        self.uploading_by_schedule_timer.timeout.connect(self.upload_by_schedule)
        self.uploading_by_schedule_timer.start(10_000)

        self.updating_accounts = QTimer(self)
        self.updating_accounts.timeout.connect(self.update_accounts)
        self.updating_accounts.start(3_000)

        self.horizontalHeader().sectionResized.connect(self.section_resized)

    def update_upload_items(self):
        for queue_media in self.queue_media_list:
            if queue_media.upload_date is None:
                if queue_media.wait_for is None:
                    queue_media.upload_date = datetime.now()

    def upload_by_schedule(self):

        if self.lock_bool is True:
            return

        self.lock_bool = True
        for queue_media in self.queue_media_list:
            wait_for = self.find_queue_media_by_id(queue_media.wait_for)
            if ((wait_for is None or wait_for.status == 2) and queue_media.upload_date is not None and
                    queue_media.upload_date < datetime.now() and queue_media.status == 0 and queue_media.video_dir != get_str('on_download')):

                queue_media.status = 1
                self.state_service.save_upload_queue_media(self.queue_media_list)

                event_loop = None

                if Hosting[queue_media.hosting].value[0].is_async():
                    event_loop = asyncio.new_event_loop()

                upload_thread = kthread.KThread(target=self.upload_video, daemon=True, args=[queue_media, queue_media.id, event_loop])

                self.upload_thread_dict[queue_media.id] = upload_thread
                upload_thread.start()
        self.lock_bool = False

    def update_accounts(self):
        for dict in self.queue_media_service.get_reauthorized_accounts_from_accounts_page():
            for queue_media in self.queue_media_list:
                if queue_media.account.url == dict[0].url and queue_media.account.login == dict[0].login and queue_media.account.hosting == dict[0].hosting:
                    queue_media.account = dict[1]
                    self.state_service.save_upload_queue_media(self.queue_media_list)
                    row = self.find_row_number_by_id(queue_media.id)

                    if dict[1].url is not None:
                        item = dict[1].url
                    else:
                        item = dict[1].login

                    self.item(row, 1).setText(item)

    def upload_video(self, queue_media, queue_media_id, event_loop):
        try:

            if exists(queue_media.video_dir) is False:
                self.set_media_status(queue_media.id, 3, 'video_not_exists')
                return

            self.set_media_status(queue_media.id, 1)

            if event_loop is not None:
                asyncio.set_event_loop(event_loop)

            name = ''
            description = ''

            if queue_media.title == '' or queue_media.title is None or queue_media.description == '' or queue_media.description is None:
                try:
                    with open(os.path.splitext(queue_media.video_dir)[0] + '.info.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        name = data['title']

                        if 'description' in data:
                            description = data['description']
                except:
                    log_error(f'{os.path.splitext(queue_media.video_dir)[0]} - .info.json не найден')
            else:
                name = queue_media.title
                description = queue_media.description

            acc = None
            for upload_account in state_service.get_accounts():
                if queue_media.account.login == upload_account.login and queue_media.account.hosting == upload_account.hosting and queue_media.account.url == upload_account.url:
                    acc = upload_account
                    break

            if acc is None:
                acc = queue_media.account

            try:
                result = Hosting[queue_media.hosting].value[0].check_auth(acc)
            except:
                log_error(traceback.format_exc())
                result = False

            if result is False:
                self.set_media_status(queue_media.id, 3, 'check_fail')
                for media in self.queue_media_list:
                    if media.id != queue_media.id and media.account.hosting == queue_media.account.hosting and media.account.url == queue_media.account.url and media.account.login == queue_media.account.login and media.status == 1:
                        if media.id in self.upload_thread_dict.keys():
                            if self.upload_thread_dict[media.id] is not None and self.upload_thread_dict[media.id].is_alive():
                                self.upload_thread_dict[media.id].terminate()
                        self.set_media_status(media.id, 0)
                return

            Hosting[queue_media.hosting].value[0].upload_video(
                file_path=queue_media.video_dir,
                account=acc,
                name=name,
                description=description,
                destination=queue_media.account.url,
                table_item=self.get_status_table_item_by_id(queue_media_id))

            rename = True

            for item in self.queue_media_list:
                if (item.hosting != queue_media.hosting or item.destination != queue_media.account.url) \
                        and item.video_dir == queue_media.video_dir and item.status != 2:
                    rename = False
                    break

            if rename and queue_media.hash is not None:
                os.renames(queue_media.video_dir,
                           queue_media.video_dir.replace(f'_{queue_media.hash}', ''))
                os.renames(os.path.splitext(queue_media.video_dir)[0] + '.info.json',
                           (os.path.splitext(queue_media.video_dir)[0] + '.info.json').replace(f'_{queue_media.hash}', ''))

                for item in self.queue_media_list:
                    if item.video_dir == queue_media.video_dir and item != queue_media:
                        item.video_dir = queue_media.video_dir.replace(f'_{queue_media.hash}', '')
                        self.item(self.find_row_number_by_id(item.id), 0).setText(item.video_dir)
                        self.update()

                for item in self.state_service.get_download_queue_media():
                    if item.video_dir == queue_media.video_dir:
                        item.video_dir = queue_media.video_dir.replace(queue_media.hash, '')
                        self.state_service.save_download_queue_media(self.state_service.get_download_queue_media())

                queue_media.video_dir = queue_media.video_dir.replace(queue_media.hash, '')


            if queue_media.remove_files_after_upload:
                for filename in glob.glob(os.path.dirname(queue_media.video_dir) + '/*'):
                    if filename.startswith(os.path.splitext(queue_media.video_dir)[0]):
                        remove = True
                        for item in self.queue_media_list:
                            if (item.hosting != queue_media.hosting or item.account != acc) \
                                    and item.video_dir == queue_media.video_dir and item.status != 2:
                                remove = False
                                break
                        if remove:
                            os.remove(filename)

        except SystemExit:
            self.set_media_status(queue_media.id, 4)
            self.upload_thread_dict.pop(queue_media.id)
            return
        except Exception as e:
            try:
                log_error(traceback.format_exc())
                if e.args[0].__contains__('Видео в слишком низком разрешении'):
                    self.set_media_status(queue_media.id, 3, 'video_in_low_resolution')
                elif e.args[0].__contains__('Необходимо активировать аккаунт'):
                    self.set_media_status(queue_media.id, 3, 'need_make_some_action_on_videohosting')
                elif e.args[0].__contains__('ERR_CONNECTION_RESET'):
                    self.set_media_status(queue_media.id, 3, 'check_internet_connection')
                elif e.args[0].__contains__('Дубликат'):
                    self.set_media_status(queue_media.id, 3, 'duplicate')
                else:
                    self.set_media_status(queue_media.id, 3, 'technical_error')
            except:
                self.set_media_status(queue_media.id, 3, 'technical_error')
            if state_service.get_settings().send_crash_notifications:
                MailService().send_log()
            return

        self.event_service.add_event(Event(
            f'{get_str("event_uploaded")} {queue_media.video_dir} {get_str("to")} {queue_media.hosting}, {queue_media.account.url if queue_media.account.url is not None else acc.login}'))
        self.set_media_status(queue_media.id, 2)

        while self.lock_bool is not False:
            pass

        self.lock_bool = True

        for media in self.queue_media_list:
            if media.wait_for == queue_media.id:
                while media.upload_date < datetime.now():
                    media.upload_date = media.upload_date + media.upload_in

        self.lock_bool = False

        self.upload_thread_dict.pop(queue_media.id)

    def update_queue_media(self):
        last_added_queue_media = self.queue_media_service.get_last_added_upload_queue_media().copy()
        last_added_temp_queue_media = self.queue_media_service.get_last_added_temp_upload_queue_media().copy()

        for queue_media in last_added_queue_media:
            self.insert_queue_media(queue_media)

        for queue_media in last_added_temp_queue_media:
            if queue_media.status == 6:
                i = self.find_row_number_by_id(queue_media.id)
                if i is not None:
                    queue_media.error_name = self.queue_media_list[i].error_name
                    queue_media.wait_for = self.queue_media_list[i].wait_for
                    queue_media.upload_in = self.queue_media_list[i].upload_in
                    queue_media.upload_date = self.queue_media_list[i].upload_date

                    self.queue_media_list[i] = queue_media
                    self.insert_queue_media(queue_media, i)
            else:
                i = self.find_row_number_by_id(queue_media.id)

                if i is not None:
                    queue_media.wait_for = self.queue_media_list[i].wait_for
                    queue_media.upload_in = self.queue_media_list[i].upload_in
                    queue_media.upload_date = self.queue_media_list[i].upload_date

                    self.queue_media_list[i] = queue_media
                    self.insert_queue_media(queue_media, i)

        self.state_service.save_upload_queue_media(self.queue_media_list)

    def find_queue_media_by_id(self, id):
        for queue_media in self.queue_media_list:
            if queue_media.id == id:
                return queue_media
        return None

    def find_row_number_by_id(self, id):
        i = 0
        for queue_media in self.queue_media_list:
            if queue_media.id == id:
                return i
            i += 1
        return None

    def insert_queue_media(self, queue_media, index=None):
        self.lock.acquire()
        upload_video_thread = None
        if index is None:
            self.insertRow(self.rowCount())
            input_position = self.rowCount() - 1
        else:
            input_position = index

        item1 = QtWidgets.QTableWidgetItem(get_str(queue_media.video_dir))
        item1.setData(11, queue_media.id)

        item3 = QtWidgets.QTableWidgetItem(queue_media.hosting)

        if queue_media.account.url is not None:
            item2 = QtWidgets.QTableWidgetItem(queue_media.account.url)
        else:
            item2 = QtWidgets.QTableWidgetItem(queue_media.account.login)

        action_button = QtWidgets.QPushButton(self)
        if queue_media.status == 0 or queue_media.status == 4:
            item4 = QtWidgets.QPushButton(get_str('stopped'))
            item4.clicked.connect(self.do_nothing)
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_upload)
        elif queue_media.status == 1:
            if state_service.get_settings().enable_autostart:
                item4 = QtWidgets.QPushButton(get_str('process'))
                item4.clicked.connect(self.do_nothing)
                action_button.setText(get_str('stop'))
                action_button.clicked.connect(self.on_stop_upload)

                if queue_media.id not in self.upload_thread_dict.keys():
                    event_loop = None

                    if Hosting[queue_media.hosting].value[0].is_async():
                        event_loop = asyncio.new_event_loop()

                    upload_video_thread = kthread.KThread(target=self.upload_video,
                                                          daemon=True,
                                                          args=[queue_media, queue_media.id, event_loop])

                    self.upload_thread_dict[queue_media.id] = upload_video_thread
            else:
                queue_media.status = 4
                self.state_service.save_upload_queue_media(self.queue_media_list)
                item4 = QtWidgets.QPushButton(get_str('stopped'))
                item4.clicked.connect(self.do_nothing)
                action_button.setText(get_str('start'))
                action_button.clicked.connect(self.on_start_upload)

        elif queue_media.status == 2:
            item4 = QtWidgets.QPushButton(get_str('end'))
            item4.clicked.connect(self.do_nothing)
            action_button.setText('-')
        elif queue_media.status == 3 or queue_media.status == 6:
            item4 = QtWidgets.QPushButton(get_str('error'))
            if queue_media.error_name is None or get_str(queue_media.error_name) == get_str('technical_error'):
                item4.clicked.connect(partial(self.show_error, get_str('technical_error')))
                action_button.setText(get_str('retry'))
                action_button.clicked.connect(self.on_start_upload)
            elif get_str(queue_media.error_name) == get_str('check_fail'):
                item4.clicked.connect(partial(self.show_error, get_str(queue_media.error_name)))
                action_button.setText(get_str('reauthorize'))
                action_button.clicked.connect(partial(self.reauthorize, queue_media))
            else:
                item4.clicked.connect(partial(self.show_error, get_str(queue_media.error_name)))
                action_button.setText('-')
                action_button.clicked.connect(self.do_nothing)

        elif queue_media.status == 5:
            item4 = QtWidgets.QPushButton(get_str('on_download'))
            item4.clicked.connect(self.do_nothing)
            action_button.setText('-')

            def do_nothing():
                return

            action_button.clicked.connect(do_nothing)

        self.setCellWidget(input_position, 4, action_button)

        delete_button = QtWidgets.QPushButton(self)
        delete_button.setText('-')
        self.setCellWidget(input_position, 5, delete_button)

        delete_button.clicked.connect(self.on_delete_row)

        self.setItem(input_position, 0, item1)
        self.setItem(input_position, 1, item2)
        self.setItem(input_position, 2, item3)
        self.setCellWidget(input_position, 3, item4)
        self.update()

        if upload_video_thread is not None:
            upload_video_thread.start()
        self.lock.release()

    def set_media_status(self, media_id, status, error_name=None):
        self.lock.acquire()

        def clicked_disconnect(i, j):
            try:
                self.cellWidget(i, j).clicked.disconnect()
            except:
                pass

        i = 0
        for media in self.queue_media_list:
            if media.id == media_id:
                media.status = status
                self.state_service.save_upload_queue_media(self.queue_media_list)
                if self.cellWidget(i, 4) is not None:
                    if status == 0 or status == 4:
                        clicked_disconnect(i, 3)
                        self.cellWidget(i, 3).clicked.connect(self.do_nothing)
                        self.cellWidget(i, 3).setText(get_str('stopped'))
                        self.cellWidget(i, 4).setText(get_str('start'))
                        clicked_disconnect(i, 4)
                        self.cellWidget(i, 4).clicked.connect(self.on_start_upload)
                    elif status == 1:
                        clicked_disconnect(i, 3)
                        self.cellWidget(i, 3).clicked.connect(self.do_nothing)
                        self.cellWidget(i, 3).setText(get_str('process'))
                        self.cellWidget(i, 4).setText(get_str('stop'))
                        clicked_disconnect(i, 4)
                        self.cellWidget(i, 4).clicked.connect(self.on_stop_upload)
                    elif status == 2:
                        clicked_disconnect(i, 3)
                        self.cellWidget(i, 3).clicked.connect(self.do_nothing)
                        self.item(i, 0).setText(media.video_dir)
                        self.cellWidget(i, 3).setText(get_str('end'))
                        self.cellWidget(i, 4).setText('-')
                        clicked_disconnect(i, 4)
                    elif status == 3:
                        clicked_disconnect(i, 3)
                        clicked_disconnect(i, 4)

                        self.cellWidget(i, 3).setText(get_str('error'))

                        if error_name is not None:
                            media.error_name = error_name
                            self.state_service.save_upload_queue_media(self.queue_media_list)
                            if get_str(error_name) == get_str(
                                    'technical_error'):
                                self.cellWidget(i, 3).clicked.connect(partial(self.show_error, get_str('technical_error')))
                                self.cellWidget(i, 4).setText(get_str('retry'))
                                self.cellWidget(i, 4).clicked.connect(self.on_start_upload)
                            elif get_str(error_name) == get_str('check_fail'):
                                self.cellWidget(i, 3).clicked.connect(partial(self.show_error, get_str(error_name)))
                                self.cellWidget(i, 4).setText(get_str('reauthorize'))
                                self.cellWidget(i, 4).clicked.connect(partial(self.reauthorize, media))
                            else:
                                self.cellWidget(i, 3).clicked.connect(partial(self.show_error, get_str(error_name)))
                                self.cellWidget(i, 4).setText('-')
                                self.cellWidget(i, 4).clicked.connect(self.do_nothing)
                        else:
                            if media.error_name is None or get_str(media.error_name) == get_str(
                                    'technical_error'):
                                self.cellWidget(i, 3).clicked.connect(partial(self.show_error, get_str('technical_error')))
                                self.cellWidget(i, 4).setText(get_str('retry'))
                                self.cellWidget(i, 4).clicked.connect(self.on_start_upload)
                            elif get_str(media.error_name) == get_str('check_fail'):
                                self.cellWidget(i, 3).clicked.connect(partial(self.show_error, get_str(media.error_name)))
                                self.cellWidget(i, 4).setText(get_str('reauthorize'))
                                self.cellWidget(i, 4).clicked.connect(partial(self.reauthorize, media))
                            else:
                                self.cellWidget(i, 3).clicked.connect(partial(self.show_error, get_str(media.error_name)))
                                self.cellWidget(i, 4).setText('-')
                                self.cellWidget(i, 4).clicked.connect(self.do_nothing)

                break
            i += 1
        self.update()
        self.lock.release()

    def reauthorize(self, media):
        hosting = Hosting[media.hosting]

        account = hosting.value[0].show_login_dialog(hosting, form=self, title='check_fail',
                                                     login=media.account.login,
                                                     password=media.account.password if self.state_service.get_settings().save_password else '',
                                                     can_relogin=True)

        if account is None:
            self.set_media_status(media.id, 3, get_str("check_fail"))
            return

        index = 0
        for acc in self.state_service.get_accounts():
            if acc.hosting == media.account.hosting and acc.login == media.account.login and acc.url == media.account.url:
                break
            index += 1

        msg = QtWidgets.QMessageBox(self)
        msg.setText(get_str('authorized_successfully'))

        if hosting.value[0].need_to_pass_channel_after_login():
            try:
                if hosting.value[0].validate_url_by_account(media.account.url, account) is False:
                    msg = QtWidgets.QMessageBox(self)
                    msg.setText(f'{get_str("failed_account_validation")}: {media.account.url}')
                    self.event_service.add_event(Event(f'{get_str("failed_account_validation")}: {media.account.url}'))
                    msg.exec_()
                    return
            except:
                msg.exec_()
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("failed_account_validation")}: {media.account.url}'))
                self.add_button.stop_animation()
                return
        msg.exec_()

        for item in self.queue_media_list:
            if item.account.login == media.account.login and item.account.hosting == media.account.hosting and item.account.url == media.account.url and item != media:
                item.account = account

                if item.status == 3:
                    self.set_media_status(item.id, 0)

                if item.account.url is not None:
                    item2 = item.account.url
                else:
                    item2 = item.account.login

                self.item(self.find_row_number_by_id(item.id), 1).setText(item2)

        self.state_service.save_upload_queue_media(self.queue_media_list)

        account.url = media.account.url
        acc_temp = media.account

        media.account = account

        if media.account.url is not None:
            item2 = media.account.url
        else:
            item2 = media.account.login

        self.item(self.find_row_number_by_id(media.id), 1).setText(item2)

        accounts = self.state_service.get_accounts()
        accounts[index] = media.account
        self.state_service.save_accounts(accounts)

        self.update()

        event_loop = None

        if Hosting[media.hosting].value[0].is_async():
            event_loop = asyncio.new_event_loop()

        self.queue_media_service.add_reauthorized_account_from_upload_page(acc_temp, account)

        upload_thread = kthread.KThread(target=self.upload_video, daemon=True,
                                        args=[media, media.id, event_loop])

        self.upload_thread_dict[media.id] = upload_thread
        upload_thread.start()

    def show_error(self, status_name):
        dialog = ShowErrorDialog(self, status_name)
        dialog.exec_()

    def do_nothing(self):
        pass

    def on_add(self):
        form = AddUploadQueueByDirectoryForm(self)
        form.exec_()

        if form.passed is True:
            prev_id = {}
            index = 0
            upload_date = form.first_upload_date
            for item in form.video_info:
                for target in item[4]:

                    id = str(uuid.uuid4())

                    wait_for = None

                    if str([target['hosting'], target['login']]) in prev_id:
                        wait_for = prev_id[str([target['hosting'], target['login']])]

                    self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=id,
                                                                                      video_dir=item[0],
                                                                                      hosting=target['hosting'],
                                                                                      status=0,
                                                                                      account=self.state_service.get_account_by_hosting_and_login(
                                                                                          target['hosting'],
                                                                                          target['login'],
                                                                                          target['upload_target']),
                                                                                      destination=target[
                                                                                          'upload_target'],
                                                                                      upload_date=None if len(form.video_info) == 1 else upload_date,
                                                                                      upload_in=form.upload_in,
                                                                                      wait_for=wait_for,
                                                                                      title=target['title'],
                                                                                      description=target['description'],
                                                                                      remove_files_after_upload=False))
                    prev_id[str([target['hosting'], target['login']])] = id
                upload_date = upload_date + form.upload_in
                index += 1

    def get_status_table_item_by_id(self, media_id):
        i = 0
        for media in self.queue_media_list:
            if media.id == media_id:
                return self.cellWidget(i, 3)
            i += 1
        return None

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            pos = self.horizontalScrollBar().sliderPosition()
            media_id = self.item(row, 0).data(11)
            self.removeRow(row)

            self.queue_media_list.pop(row)

            self.state_service.save_upload_queue_media(self.queue_media_list)

            if media_id in self.upload_thread_dict:
                if self.upload_thread_dict[media_id] is not None and self.upload_thread_dict[media_id].is_alive():
                    self.upload_thread_dict[media_id].terminate()
                self.upload_thread_dict[media_id] = None
            self.horizontalScrollBar().setSliderPosition(pos)

    # Функции для кнопок остановить и начать
    def on_stop_upload(self):
        button = self.sender()
        if button:
            time.sleep(0.2)
            row = self.indexAt(button.pos()).row()
            media_id = self.item(row, 0).data(11)

            self.set_media_status(media_id, 4)

            if media_id in self.upload_thread_dict:
                if self.upload_thread_dict[media_id] is not None and self.upload_thread_dict[media_id].is_alive():
                    self.upload_thread_dict[media_id].terminate()
                self.upload_thread_dict[media_id] = None

    def on_start_upload(self):
        button = self.sender()
        if button:
            time.sleep(0.2)
            row = self.indexAt(button.pos()).row()
            media_id = self.item(row, 0).data(11)

            for media in self.queue_media_list:
                if media.id == media_id:
                    event_loop = None

                    media.status = 1
                    self.state_service.save_upload_queue_media(self.queue_media_list)

                    if Hosting[media.hosting].value[0].is_async():
                        event_loop = asyncio.new_event_loop()

                    upload_video_thread = kthread.KThread(target=self.upload_video, daemon=True,
                                                          args=[media, media.id, event_loop])

                    self.upload_thread_dict[media_id] = upload_video_thread
                    upload_video_thread.start()

    change = True

    def section_resized(self, index, width):
        if self.change:
            coef_x = self.parent().width() / 950
            self.state_service.save_column_row('upload', index, int(width / coef_x))

    def resizeEvent(self, event):
        self.change = False
        coef_x = self.parent().width() / 950

        if self.state_service.column_row('upload', 0) is None or self.state_service.column_row('upload', 1) is None or self.state_service.column_row('upload', 2) is None or self.state_service.column_row('upload', 3) is None or self.state_service.column_row('upload', 4) is None or self.state_service.column_row('upload', 5) is None:
            column_width = int(950 / 6)

            if self.state_service.column_row('upload', 0) is None:
                self.state_service.save_column_row('upload', 0, column_width)
            if self.state_service.column_row('upload', 1) is None:
                self.state_service.save_column_row('upload', 1, column_width)
            if self.state_service.column_row('upload', 2) is None:
                self.state_service.save_column_row('upload', 2, column_width)
            if self.state_service.column_row('upload', 3) is None:
                self.state_service.save_column_row('upload', 3, column_width)
            if self.state_service.column_row('upload', 4) is None:
                self.state_service.save_column_row('upload', 4, column_width)
            if self.state_service.column_row('upload', 5) is None:
                self.state_service.save_column_row('upload', 5, column_width)

        width_0 = int(self.state_service.column_row('upload', 0) * coef_x)
        width_1 = int(self.state_service.column_row('upload', 1) * coef_x)
        width_2 = int(self.state_service.column_row('upload', 2) * coef_x)
        width_3 = int(self.state_service.column_row('upload', 3) * coef_x)
        width_4 = int(self.state_service.column_row('upload', 4) * coef_x)
        width_5 = int(self.state_service.column_row('upload', 5) * coef_x)

        self.setColumnWidth(0, width_0)
        self.setColumnWidth(1, width_1)
        self.setColumnWidth(2, width_2)
        self.setColumnWidth(3, width_3)
        self.setColumnWidth(4, width_4)
        self.setColumnWidth(5, width_5)

        self.change = True

        return super(UploadQueuePageWidget, self).resizeEvent(event)
