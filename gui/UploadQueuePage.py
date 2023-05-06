from PyQt5 import QtCore, QtWidgets

from service.StateService import StateService
from service.QueueMediaService import QueueMediaService
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
        item.setText(_translate("BuharVideoUploader", "Видео"))
        item = self.horizontalHeaderItem(1)
        item.setText(_translate("BuharVideoUploader", "Источник выгрузки"))
        item = self.horizontalHeaderItem(2)
        item.setText(_translate("BuharVideoUploader", "Статус"))
        item = self.horizontalHeaderItem(3)
        item.setText(_translate("BuharVideoUploader", "Действие"))
        item = self.horizontalHeaderItem(4)
        item.setText(_translate("BuharVideoUploader", "Удалить"))

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
            self.set_media_status(queue_media.video_dir, 1, 'Процесс')
            Hosting[queue_media.hosting].value[0].upload_video(
                file_path=queue_media.video_dir,
                account=queue_media.account)
        except:
            log_error(traceback.format_exc())
            self.set_media_status(queue_media.video_dir, 3, 'Ошибка')

        self.set_media_status(queue_media.video_dir, 2, 'Завершено')
        self.download_thread_dict.pop(queue_media.video_dir)

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
            item2 = QtWidgets.QTableWidgetItem(f'Аккаунт: {queue_media.account.login}')

        if queue_media.status == 0:
            item3 = QtWidgets.QTableWidgetItem('Пауза')
        elif queue_media.status == 1:
            if self.download_thread_dict[queue_media.url] is None:
                item3 = QtWidgets.QTableWidgetItem('Пауза')
            else:
                item3 = QtWidgets.QTableWidgetItem('Процесс')
        elif queue_media.status == 2:
            item3 = QtWidgets.QTableWidgetItem('Завершено')
        else:
            item3 = QtWidgets.QTableWidgetItem('Ошибка')

        action_button = QtWidgets.QPushButton(self)
        action_button.setText('+')
        self.setCellWidget(input_position, 4, action_button)

        delete_button = QtWidgets.QPushButton(self)
        delete_button.setText('-')
        self.setCellWidget(input_position, 5, delete_button)

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
