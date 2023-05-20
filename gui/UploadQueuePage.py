import asyncio
import time

from PyQt5 import QtCore, QtWidgets

from model.Event import Event
from model.UploadQueueMedia import UploadQueueMedia
from service.EventService import EventService
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


class UploadQueuePageWidget(QtWidgets.QTableWidget):
    state_service = StateService()
    event_service = EventService()
    queue_media_service = QueueMediaService()
    queue_media_list = state_service.get_upload_queue_media()
    settings = state_service.get_settings()
    upload_thread_dict = {}

    def __init__(self, central_widget):
        super(UploadQueuePageWidget, self).__init__(central_widget)
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

    def upload_by_schedule(self):
        for queue_media in self.queue_media_list:
            if queue_media.upload_date is not None and queue_media.upload_date < datetime.now() \
                    and queue_media.status == 0:

                time.sleep(5)

                queue_media.status = 1
                self.state_service.save_upload_queue_media(self.queue_media_list)

                event_loop = None

                if Hosting[queue_media.hosting].value[0].is_async():
                    event_loop = asyncio.new_event_loop()

                upload_thread = kthread.KThread(target=self.upload_video, daemon=True, args=[queue_media, event_loop])

                key_part = queue_media.destination if queue_media.destination is not None else queue_media.account.login

                self.upload_thread_dict[
                    frozenset({queue_media.video_dir, key_part, queue_media.hosting})] = upload_thread
                upload_thread.start()

    def upload_video(self, queue_media, event_loop):
        time.sleep(3)
        key_part = queue_media.destination if queue_media.destination is not None else queue_media.account.login
        key = frozenset({queue_media.video_dir, key_part, queue_media.hosting})

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
                    log_error(f'{queue_media.video_dir} - .info.json не найден')
            else:
                name = queue_media.title
                description = queue_media.description

            self.set_media_status(key, 1)
            Hosting[queue_media.hosting].value[0].upload_video(
                file_path=queue_media.video_dir,
                account=queue_media.account,
                name=name,
                description=description,
                destination=queue_media.destination)

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
            self.set_media_status(key, 4)
            self.upload_thread_dict.pop(key)
            return
        except Exception:
            log_error(traceback.format_exc())
            self.set_media_status(key, 3)
            return

        self.event_service.add_event(Event(f'{get_str("event_uploaded")} {queue_media.video_dir} {get_str("to")} {queue_media.hosting}, {key_part}'))
        self.set_media_status(key, 2)
        self.upload_thread_dict.pop(key)

    def update_queue_media(self):
        last_added_queue_media = self.queue_media_service.get_last_added_upload_queue_media()
        for queue_media in last_added_queue_media:
            self.insert_queue_media(queue_media)

        last_added_temp_queue_media = self.queue_media_service.get_last_added_temp_upload_queue_media()
        for queue_media in last_added_temp_queue_media:
            i = self.find_row_number_by_login_and_hosting(queue_media.account.login, queue_media.hosting,
                                                          queue_media.destination)
            if i is not None:
                self.insert_queue_media(queue_media, i)

    def find_row_number_by_login_and_hosting(self, login, hosting, target):
        for i in range(0, self.rowCount()):
            if (self.item(i, 1).text() == login or self.item(i, 1) == target) and self.item(i, 2).text() == hosting \
                    and self.item(i, 3).text() == get_str('on_download'):
                return i
        return None

    def insert_queue_media(self, queue_media, index=None):

        if index is None:
            self.insertRow(self.rowCount())
            input_position = self.rowCount() - 1
        else:
            input_position = index

        item1 = QtWidgets.QTableWidgetItem(queue_media.video_dir)

        item3 = QtWidgets.QTableWidgetItem(queue_media.hosting)

        if queue_media.destination is not None:
            item2 = QtWidgets.QTableWidgetItem(queue_media.destination)
        else:
            item2 = QtWidgets.QTableWidgetItem(queue_media.account.login)

        action_button = QtWidgets.QPushButton(self)
        if queue_media.status == 0 or queue_media.status == 4:
            item4 = QtWidgets.QTableWidgetItem(get_str('stopped'))
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_upload)
        elif queue_media.status == 1:
            item4 = QtWidgets.QTableWidgetItem(get_str('process'))
            action_button.setText(get_str('stop'))
            action_button.clicked.connect(self.on_stop_upload)

            key_part = queue_media.destination if queue_media.destination is not None else queue_media.account.login
            key = frozenset({queue_media.video_dir, key_part, queue_media.hosting})
            if key not in self.upload_thread_dict.keys():
                event_loop = None

                if Hosting[queue_media.hosting].value[0].is_async():
                    event_loop = asyncio.new_event_loop()

                upload_video_thread = kthread.KThread(target=self.upload_video,
                                                      daemon=True,
                                                      args=[queue_media, event_loop])

                self.upload_thread_dict[key] = upload_video_thread
                upload_video_thread.start()

        elif queue_media.status == 2:
            item4 = QtWidgets.QTableWidgetItem(get_str('end'))
            action_button.setText('-')
        elif queue_media.status == 3:
            item4 = QtWidgets.QTableWidgetItem(get_str('error'))
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_upload)
        elif queue_media.status == 5:
            item4 = QtWidgets.QTableWidgetItem(get_str('on_download'))
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
        self.setItem(input_position, 3, item4)

    def set_media_status(self, key, status):
        i = 0
        time.sleep(0.2)
        for media in self.queue_media_list:
            if media.video_dir in key and media.hosting in key and (
                    media.destination in key or media.account.login in key) and (
                    media.account.login in key or media.destination in key):
                media.status = status
                self.state_service.save_upload_queue_media(self.queue_media_list)

                if status == 0 or status == 4:
                    self.item(i, 3).setText(get_str('stopped'))
                    self.cellWidget(i, 4).setText(get_str('start'))
                    self.cellWidget(i, 4).clicked.disconnect()
                    self.cellWidget(i, 4).clicked.connect(self.on_start_upload)
                elif status == 1:
                    self.item(i, 3).setText(get_str('process'))
                    self.cellWidget(i, 4).setText(get_str('stop'))
                    self.cellWidget(i, 4).clicked.disconnect()
                    self.cellWidget(i, 4).clicked.connect(self.on_stop_upload)
                elif status == 2:
                    self.item(i, 3).setText(get_str('end'))
                    self.cellWidget(i, 4).setText('-')
                    self.cellWidget(i, 4).clicked.disconnect()
                elif status == 3:
                    self.item(i, 3).setText(get_str('error'))
                    self.cellWidget(i, 4).setText(get_str('start'))
                    self.cellWidget(i, 4).clicked.disconnect()
                    self.cellWidget(i, 4).clicked.connect(self.on_start_upload)
                break
            i += 1

    def get_row_index(self, video_dir):
        i = 0
        for media in self.queue_media_list:
            if media.video_dir == video_dir:
                return i
            i += 1

    def on_add(self):
        form = AddUploadQueueByDirectoryForm(self)
        form.exec_()

        if form.passed is True:
            for item in form.video_info:
                for target in item[4]:
                    self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(video_dir=item[0],
                                                                                      hosting=target['hosting'],
                                                                                      status=0,
                                                                                      account=self.state_service.get_account_by_hosting_and_login(target['hosting'], target['login']),
                                                                                      destination=target['upload_target'],
                                                                                      upload_date=item[3],
                                                                                      title=item[1],
                                                                                      description=item[2],
                                                                                      remove_files_after_upload=False))

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            video_dir = self.item(row, 0).text()
            destination = self.item(row, 1).text()
            hosting = self.item(row, 2).text()
            self.removeRow(row)

            self.queue_media_list.pop(row)

            self.state_service.save_upload_queue_media(self.queue_media_list)

            key = frozenset({video_dir, destination, hosting})

            if key in self.upload_thread_dict:
                if self.upload_thread_dict[key] is not None and self.upload_thread_dict[key].is_alive():
                    self.upload_thread_dict[key].terminate()
                self.upload_thread_dict[key] = None

    # Функции для кнопок остановить и начать
    def on_stop_upload(self):
        button = self.sender()
        if button:
            time.sleep(0.2)
            row = self.indexAt(button.pos()).row()
            video_dir = self.item(row, 0).text()
            destination = self.item(row, 1).text()
            hosting = self.item(row, 2).text()

            key = frozenset({video_dir, destination, hosting})

            self.set_media_status(key, 4)

            if key in self.upload_thread_dict:
                if self.upload_thread_dict[key] is not None and self.upload_thread_dict[key].is_alive():
                    self.upload_thread_dict[key].terminate()
                self.upload_thread_dict[key] = None

    def on_start_upload(self):
        button = self.sender()
        if button:
            time.sleep(0.2)
            row = self.indexAt(button.pos()).row()
            video_dir = self.item(row, 0).text()
            destination = self.item(row, 1).text()
            hosting = self.item(row, 2).text()

            key = frozenset({video_dir, destination, hosting})

            self.set_media_status(key, 1)

            for media in self.queue_media_list:
                if media.video_dir == video_dir and \
                        (media.account.login == destination or media.destination == destination) \
                        and media.hosting == hosting:
                    event_loop = None

                    if Hosting[media.hosting].value[0].is_async():
                        event_loop = asyncio.new_event_loop()

                    upload_video_thread = kthread.KThread(target=self.upload_video, daemon=True,
                                                          args=[media, event_loop])

                    self.upload_thread_dict[key] = upload_video_thread
                    upload_video_thread.start()
