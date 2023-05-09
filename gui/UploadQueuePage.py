import os.path
from PyQt5 import QtCore, QtWidgets

from service.QueueMediaService import QueueMediaService
from service.LocalizationService import *
from model.Hosting import Hosting
from threading import Thread
from PyQt5.QtCore import QTimer
from service.LoggingService import *
import traceback
from datetime import datetime


class UploadQueuePageWidget(QtWidgets.QTableWidget):

    state_service = StateService()
    queue_media_service = QueueMediaService()
    queue_media_list = state_service.get_upload_queue_media()
    settings = state_service.get_settings()
    upload_thread_dict = {}

    def __init__(self, central_widget):
        _translate = QtCore.QCoreApplication.translate

        super(UploadQueuePageWidget, self).__init__(central_widget)
        self.setMinimumSize(QtCore.QSize(0, 440))
        self.setObjectName("upload_queue_page_widget")
        self.setColumnCount(5)
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
        self.horizontalHeader().setDefaultSectionSize(186)

        _translate = QtCore.QCoreApplication.translate
        item = self.horizontalHeaderItem(0)
        item.setText(get_str('video'))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str('upload_target'))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str('status'))
        item = self.horizontalHeaderItem(3)
        item.setText(get_str('action'))
        item = self.horizontalHeaderItem(4)
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
                queue_media.status = 1
                self.state_service.save_upload_queue_media(self.queue_media_list)
                upload_thread = Thread(target=self.upload_video, daemon=True, args=[queue_media])

                self.upload_thread_dict[queue_media.video_dir] = upload_thread
                upload_thread.start()

    def upload_video(self, queue_media):
        try:

            name = ''
            description = ''

            try:
                f = open(os.path.splitext(queue_media.video_dir)[0] + '.info.json')
                data = json.load(f)

                name = data['title']

                if 'description' in data:
                    description = data['description']

            except:
                log_error(f'{queue_media.video_dir} - .info.json не найден')

            self.set_media_status(queue_media.video_dir, 1, get_str('process'))
            Hosting[queue_media.hosting].value[0].upload_video(
                file_path=queue_media.video_dir,
                account=queue_media.account,
                name=name,
                description=description)
        except:
            log_error(traceback.format_exc())
            self.set_media_status(queue_media.video_dir, 3, get_str('error'))
            return

        self.set_media_status(queue_media.video_dir, 2, get_str('end'))
        self.upload_thread_dict.pop(queue_media.video_dir)

    def update_queue_media(self):
        last_added_queue_media = self.queue_media_service.get_last_added_upload_queue_media()
        for queue_media in last_added_queue_media:
            self.insert_queue_media(queue_media)

    def insert_queue_media(self, queue_media):
        self.insertRow(self.rowCount())
        input_position = self.rowCount() - 1

        item1 = QtWidgets.QTableWidgetItem(queue_media.video_dir)

        if queue_media.destination is not None:
            item2 = QtWidgets.QTableWidgetItem(queue_media.destination)
        else:
            item2 = QtWidgets.QTableWidgetItem(f'{get_str("account")}: {queue_media.account.login}')

        if queue_media.status == 0:
            item3 = QtWidgets.QTableWidgetItem(get_str('pause'))
        elif queue_media.status == 1:
            item3 = QtWidgets.QTableWidgetItem(get_str('process'))

            if queue_media.video_dir not in self.upload_thread_dict.keys():
                upload_thread = Thread(target=self.upload_video, daemon=True, args=[queue_media])
                self.upload_thread_dict[queue_media.video_dir] = upload_thread
                upload_thread.start()

        elif queue_media.status == 2:
            item3 = QtWidgets.QTableWidgetItem(get_str('end'))
        else:
            item3 = QtWidgets.QTableWidgetItem(get_str('error'))

        action_button = QtWidgets.QPushButton(self)
        action_button.setText('+')
        self.setCellWidget(input_position, 3, action_button)

        delete_button = QtWidgets.QPushButton(self)
        delete_button.setText('-')
        self.setCellWidget(input_position, 4, delete_button)

        delete_button.clicked.connect(self.on_delete_row)

        self.setItem(input_position, 0, item1)
        self.setItem(input_position, 1, item2)
        self.setItem(input_position, 2, item3)

    def set_media_status(self, video_dir, status, status_name):
        i = 0
        for media in self.queue_media_list:
            if media.video_dir == video_dir:
                media.status = status
                self.state_service.save_upload_queue_media(self.queue_media_list)
                self.item(i, 2).setText(status_name)
                break
            i += 1

    def get_row_index(self, video_dir):
        i = 0
        for media in self.queue_media_list:
            if media.video_dir == video_dir:
                return i
            i += 1

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            self.removeRow(row)
            video_dir = self.queue_media_list.pop(row).video_dir
            self.state_service.save_upload_queue_media(self.queue_media_list)
            if video_dir in self.upload_thread_dict:
                self.upload_thread_dict[video_dir].join()
                del self.upload_thread_dict[video_dir]
