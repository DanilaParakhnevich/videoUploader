from PyQt5 import QtCore, QtWidgets

from service.StateService import StateService
from service.QueueMediaService import QueueMediaService
from model.Hosting import Hosting
from threading import Thread
from PyQt5.QtCore import QTimer
from service.LoggingService import *
import traceback


class DownloadQueuePageWidget(QtWidgets.QTableWidget):

    state_service = StateService()
    queue_media_service = QueueMediaService()
    queue_media_list = state_service.get_queue_media()
    settings = state_service.get_settings()
    download_thread_dict = {}

    def __init__(self, central_widget):
        _translate = QtCore.QCoreApplication.translate

        super(DownloadQueuePageWidget, self).__init__(central_widget)
        self.setMinimumSize(QtCore.QSize(0, 440))
        self.setObjectName("download_queue_page_widget")
        self.setColumnCount(4)
        self.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(3, item)
        self.horizontalHeader().setDefaultSectionSize(232)

        _translate = QtCore.QCoreApplication.translate
        item = self.horizontalHeaderItem(0)
        item.setText(_translate("BuharVideoUploader", "Ссылка"))
        item = self.horizontalHeaderItem(1)
        item.setText(_translate("BuharVideoUploader", "Статус"))
        item = self.horizontalHeaderItem(2)
        item.setText(_translate("BuharVideoUploader", "Действие"))
        item = self.horizontalHeaderItem(3)
        item.setText(_translate("BuharVideoUploader", "Удалить"))

        for queue_media in self.queue_media_list:
            self.insert_queue_media(queue_media)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_queue_media)
        self.timer.start(3_000)

        if self.settings.download_strategy == 1:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.downloading_serial_hook)
            self.timer.start(3_000)
        elif self.settings.download_strategy == 2:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.downloading_parallel_hook)
            self.timer.start(3_000)

    def downloading_serial_hook(self):
        if len(self.download_thread_dict) == 0:
            for media in self.queue_media_list:
                if len(self.download_thread_dict) == 0 and media.status == 0:
                    media.status = 1
                    self.state_service.save_queue_media(self.queue_media_list)
                    download_video_thread = Thread(target=self.download_video, daemon=True, args=[media.url, media.account, media.hosting])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()

    def downloading_parallel_hook(self):
        if len(self.download_thread_dict) < self.settings.pack_count:
            for media in self.queue_media_list:
                if len(self.download_thread_dict) < self.settings.pack_count and media.status == 0:
                    media.status = 1
                    self.state_service.save_queue_media(self.queue_media_list)
                    download_video_thread = Thread(target=self.download_video, daemon=True, args=[media.url, media.account, media.hosting])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()

    def download_video(self, url, account, hosting):
        try:
            self.set_media_status(url, 1, 'Процесс')
            Hosting[hosting].value[0].download_video(
                url=url,
                account=account,
                table_item=self.item(self.get_row_index(url), 1))

        except:
            log_error(traceback.format_exc())
            self.set_media_status(url, 3, 'Ошибка')

        self.set_media_status(url, 2, 'Завершено')
        self.download_thread_dict.pop(url)

    def update_queue_media(self):
        last_added_queue_media = self.queue_media_service.get_last_added_queue_media()
        for queue_media in last_added_queue_media:
            self.insert_queue_media(queue_media)

    def insert_queue_media(self, queue_media):
        self.insertRow(self.rowCount())
        input_position = self.rowCount() - 1

        item1 = QtWidgets.QTableWidgetItem(queue_media.url)
        if queue_media.status == 0:
            item2 = QtWidgets.QTableWidgetItem('Пауза')
        elif queue_media.status == 1:
            if self.download_thread_dict[queue_media.url] is None:
                item2 = QtWidgets.QTableWidgetItem('Пауза')
            else:
                item2 = QtWidgets.QTableWidgetItem('Процесс')
        elif queue_media.status == 2:
            item2 = QtWidgets.QTableWidgetItem('Завершено')
        else:
            item2 = QtWidgets.QTableWidgetItem('Ошибка')

        action_button = QtWidgets.QPushButton(self)
        action_button.setText('+')
        self.setCellWidget(input_position, 2, action_button)

        delete_button = QtWidgets.QPushButton(self)
        delete_button.setText('-')
        self.setCellWidget(input_position, 3, delete_button)

        delete_button.clicked.connect(self.on_delete_row)

        self.setItem(input_position, 0, item1)
        self.setItem(input_position, 1, item2)

    def set_media_status(self, url, status, status_name):
        i = 0
        for media in self.queue_media_list:
            if media.url == url:
                media.status = status
                self.state_service.save_queue_media(self.queue_media_list)
                self.item(i, 1).setText(status_name)
                break
            i += 1

    def get_row_index(self, url):
        i = 0
        for media in self.queue_media_list:
            if media.url == url:
                return i
            i += 1

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            self.removeRow(row)
            url = self.queue_media_list.pop(row).url
            self.state_service.save_queue_media(self.queue_media_list)
            if url in self.download_thread_dict:
                self.download_thread_dict[url].join()
                del self.download_thread_dict[url]
