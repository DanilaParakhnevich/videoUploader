import asyncio
import time
import uuid
from functools import partial
from threading import Lock

from PyQt5 import QtCore, QtWidgets

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

    def __init__(self, central_widget):
        super(UploadQueuePageWidget, self).__init__(central_widget)
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

        self.updating_timer = QTimer(self)
        self.updating_timer.timeout.connect(self.update_queue_media)
        self.updating_timer.start(3_000)

        self.uploading_by_schedule_timer = QTimer(self)
        self.uploading_by_schedule_timer.timeout.connect(self.upload_by_schedule)
        self.uploading_by_schedule_timer.start(10_000)

        self.horizontalHeader().sectionResized.connect(self.section_resized)

    def upload_by_schedule(self):
        for queue_media in self.queue_media_list:
            if queue_media.upload_date is not None and queue_media.upload_date < datetime.now() \
                    and queue_media.status == 0:

                queue_media.status = 1
                self.state_service.save_upload_queue_media(self.queue_media_list)

                event_loop = None

                if Hosting[queue_media.hosting].value[0].is_async():
                    event_loop = asyncio.new_event_loop()

                upload_thread = kthread.KThread(target=self.upload_video, daemon=True, args=[queue_media, queue_media.id, event_loop])

                self.upload_thread_dict[queue_media.id] = upload_thread
                upload_thread.start()

    def upload_video(self, queue_media, queue_media_id, event_loop):
        try:
            if event_loop is not None:
                asyncio.set_event_loop(event_loop)

            name = ''
            description = ''

            if queue_media.title is None and queue_media.description is None:
                try:
                    f = open(os.path.splitext(queue_media.video_dir)[0] + '.info.json')
                    data = json.load(f)

                    name = data['title']

                    if 'description' in data:
                        description = data['description']

                except:
                    log_error(f'{os.path.splitext(queue_media.video_dir)[0]} - .info.json не найден')
            else:
                name = queue_media.title
                description = queue_media.description

            self.set_media_status(queue_media.id, 1)
            result = Hosting[queue_media.hosting].value[0].check_auth(queue_media.account)
            if result is False:
                self.set_media_status(queue_media.id, 3, 'check_fail')
                return
            Hosting[queue_media.hosting].value[0].upload_video(
                file_path=queue_media.video_dir,
                account=queue_media.account,
                name=name,
                description=description,
                destination=queue_media.destination,
                table_item=self.get_status_table_item_by_id(queue_media_id))

            if queue_media.remove_files_after_upload:
                for filename in glob.glob(os.path.dirname(queue_media.video_dir) + '/*'):
                    if filename.startswith(os.path.splitext(queue_media.video_dir)[0]):
                        remove = True
                        for item in self.queue_media_list:
                            if (item.hosting != queue_media.hosting or item.account != queue_media.account) \
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
            log_error(traceback.format_exc())
            if e.args[0].__contains__('Видео в слишком низком разрешении'):
                self.set_media_status(queue_media.id, 3, 'video_in_low_resolution')
            elif e.args[0].__contains__('Необходимо активировать аккаунт'):
                self.set_media_status(queue_media.id, 3, 'need_make_some_action_on_videohosting')
            else:
                self.set_media_status(queue_media.id, 3, 'technical_error')
            if state_service.get_settings().send_crash_notifications:
                MailService().send_log()
            return

        self.event_service.add_event(Event(
            f'{get_str("event_uploaded")} {queue_media.video_dir} {get_str("to")} {queue_media.hosting}, {queue_media.destination if queue_media.destination is not None else queue_media.account.login}'))
        self.set_media_status(queue_media.id, 2)
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
                    self.queue_media_list[i] = queue_media
                    self.insert_queue_media(queue_media, i)
            else:
                i = self.find_row_number_by_id(queue_media.id)

                if i is not None:
                    self.queue_media_list[i] = queue_media
                    self.insert_queue_media(queue_media, i)

        self.state_service.save_upload_queue_media(self.queue_media_list)

    def find_row_number_by_id(self, id):
        i = 0
        for queue_media in self.queue_media_list:
            if queue_media.id == id:
                return i
            i += 1
        return None

    def insert_queue_media(self, queue_media, index=None):
        upload_video_thread = None
        if index is None:
            self.insertRow(self.rowCount())
            input_position = self.rowCount() - 1
        else:
            input_position = index

        item1 = QtWidgets.QTableWidgetItem(get_str(queue_media.video_dir))
        item1.setData(11, queue_media.id)

        item3 = QtWidgets.QTableWidgetItem(queue_media.hosting)

        if queue_media.destination is not None:
            item2 = QtWidgets.QTableWidgetItem(queue_media.destination)
        else:
            item2 = QtWidgets.QTableWidgetItem(queue_media.account.login)

        action_button = QtWidgets.QPushButton(self)
        if queue_media.status == 0 or queue_media.status == 4:
            item4 = QtWidgets.QPushButton(get_str('stopped'))
            item4.clicked.connect(self.do_nothing)
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_upload)
        elif queue_media.status == 1:
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

    def set_media_status(self, media_id, status, error_name=None):
        self.lock.acquire()
        i = 0
        for media in self.queue_media_list:
            if media.id == media_id:
                media.status = status
                self.state_service.save_upload_queue_media(self.queue_media_list)
                if self.cellWidget(i, 4) is not None:
                    if status == 0 or status == 4:
                        self.cellWidget(i, 3).clicked.disconnect()
                        self.cellWidget(i, 3).clicked.connect(self.do_nothing)
                        self.cellWidget(i, 3).setText(get_str('stopped'))
                        self.cellWidget(i, 4).setText(get_str('start'))
                        self.cellWidget(i, 4).clicked.disconnect()
                        self.cellWidget(i, 4).clicked.connect(self.on_start_upload)
                    elif status == 1:
                        self.cellWidget(i, 3).clicked.disconnect()
                        self.cellWidget(i, 3).clicked.connect(self.do_nothing)
                        self.cellWidget(i, 3).setText(get_str('process'))
                        self.cellWidget(i, 4).setText(get_str('stop'))
                        self.cellWidget(i, 4).clicked.disconnect()
                        self.cellWidget(i, 4).clicked.connect(self.on_stop_upload)
                    elif status == 2:
                        self.cellWidget(i, 3).clicked.disconnect()
                        self.cellWidget(i, 3).clicked.connect(self.do_nothing)
                        self.cellWidget(i, 3).setText(get_str('end'))
                        self.cellWidget(i, 4).setText('-')
                        self.cellWidget(i, 4).clicked.disconnect()
                    elif status == 3:
                        if error_name is not None:
                            self.cellWidget(i, 3).clicked.disconnect()
                            self.cellWidget(i, 3).clicked.connect(partial(self.show_error, get_str(error_name)))
                            self.cellWidget(i, 3).setText(get_str('error'))
                            self.queue_media_list[i].error_name = error_name
                            self.state_service.save_upload_queue_media(self.queue_media_list)
                        else:
                            self.cellWidget(i, 3).clicked.disconnect()
                            self.cellWidget(i, 3).clicked.connect(self.do_nothing)
                            self.cellWidget(i, 3).setText(get_str('error'))

                        if error_name is None or get_str(error_name) == get_str('technical_error'):
                            self.cellWidget(i, 4).setText(get_str('retry'))
                            self.cellWidget(i, 4).clicked.disconnect()
                            self.cellWidget(i, 4).clicked.connect(self.on_start_upload)
                        else:
                            self.cellWidget(i, 4).setText('-')
                            self.cellWidget(i, 4).clicked.disconnect()
                            self.cellWidget(i, 4).clicked.connect(self.do_nothing)

                break
            i += 1
        self.update()
        self.lock.release()

    def show_error(self, status_name):
        dialog = ShowErrorDialog(self, status_name)
        dialog.exec_()

    def do_nothing(self):
        pass

    def on_add(self):
        form = AddUploadQueueByDirectoryForm(self)
        form.exec_()

        if form.passed is True:
            for item in form.video_info:
                for target in item[4]:
                    self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(uuid.uuid4()),
                                                                                      video_dir=item[0],
                                                                                      hosting=target['hosting'],
                                                                                      status=0,
                                                                                      account=self.state_service.get_account_by_hosting_and_login(
                                                                                          target['hosting'],
                                                                                          target['login']),
                                                                                      destination=target[
                                                                                          'upload_target'],
                                                                                      upload_date=item[3],
                                                                                      title=item[1],
                                                                                      description=item[2],
                                                                                      remove_files_after_upload=False))

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

            self.set_media_status(media_id, 1)

            for media in self.queue_media_list:
                if media.id == media_id:
                    event_loop = None

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
