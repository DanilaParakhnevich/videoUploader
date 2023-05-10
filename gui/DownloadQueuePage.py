from PyQt5 import QtCore, QtWidgets

from service.QueueMediaService import QueueMediaService
from model.Hosting import Hosting
from model.UploadQueueMedia import UploadQueuedMedia
from threading import Thread
from PyQt5.QtCore import QTimer
from service.LoggingService import *
from service.LocalizationService import *
import traceback
import time


class DownloadQueuePageWidget(QtWidgets.QTableWidget):

    state_service = StateService()
    queue_media_service = QueueMediaService()
    queue_media_list = state_service.get_download_queue_media()
    settings = state_service.get_settings()
    download_thread_dict = {}

    def __init__(self, central_widget):
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

        item = self.horizontalHeaderItem(0)
        item.setText(get_str('link'))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str('status'))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str('action'))
        item = self.horizontalHeaderItem(3)
        item.setText(get_str('delete'))

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
                    self.state_service.save_download_queue_media(self.queue_media_list)
                    download_video_thread = Thread(target=self.download_video, daemon=True, args=[media])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()

    def downloading_parallel_hook(self):
        if len(self.download_thread_dict) < self.settings.pack_count:
            for media in self.queue_media_list:
                if len(self.download_thread_dict) < self.settings.pack_count and media.status == 0:
                    download_video_thread = Thread(target=self.download_video, daemon=True, args=[media])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()
                    media.status = 1
                    self.state_service.save_download_queue_media(self.queue_media_list)

    def download_video(self, media):
        try:
            time.sleep(3)

            self.set_media_status(media.url, 1, get_str('process'))
            video_dir = Hosting[media.hosting].value[0].download_video(
                url=media.url,
                account=media.account,
                hosting=media.hosting,
                table_item=self.item(self.get_row_index(media.url), 1))
            if media.upload_after_download:
                self.queue_media_service.add_to_the_upload_queue(UploadQueuedMedia(video_dir=video_dir,
                                                                                   hosting=media.upload_account.hosting,
                                                                                   status=0,
                                                                                   account=media.upload_account,
                                                                                   destination=media.upload_destination,
                                                                                   upload_date=media.upload_date))

        except:
            log_error(traceback.format_exc())
            self.set_media_status(media.url, 3, get_str('error'))

        self.set_media_status(media.url, 2, get_str('end'))
        self.download_thread_dict.pop(media.url)

    def update_queue_media(self):
        last_added_queue_media = self.queue_media_service.get_last_added_download_queue_media()
        for queue_media in last_added_queue_media:
            self.insert_queue_media(queue_media)

    def insert_queue_media(self, queue_media):
        self.insertRow(self.rowCount())
        input_position = self.rowCount() - 1

        item1 = QtWidgets.QTableWidgetItem(queue_media.url)
        action_button = QtWidgets.QPushButton(self)
        if queue_media.status == 0:
            item2 = QtWidgets.QTableWidgetItem(get_str('pause'))
            action_button.setText('+')
        elif queue_media.status == 1:
            item2 = QtWidgets.QTableWidgetItem(get_str('process'))
            action_button.setText('+')
            # action_button.clicked.connect(self.start_download)
            # action_button.clicked.connect(self)

            if queue_media.url not in self.download_thread_dict.keys():
                download_video_thread = Thread(target=self.download_video, daemon=True, args=[queue_media])
                self.download_thread_dict[queue_media.url] = download_video_thread
                download_video_thread.start()

        elif queue_media.status == 2:
            item2 = QtWidgets.QTableWidgetItem(get_str('end'))
            action_button.setText('+')
            # action_button.clicked.connect()
        else:
            item2 = QtWidgets.QTableWidgetItem(get_str('error'))
            action_button.setText('+')
            # action_button.clicked.connect()

        self.setCellWidget(input_position, 2, action_button)

        delete_button = QtWidgets.QPushButton(self)
        delete_button.setText('-')
        self.setCellWidget(input_position, 3, delete_button)

        delete_button.clicked.connect(self.on_delete_row)

        self.setItem(input_position, 0, item1)
        self.setItem(input_position, 1, item2)

    def start_download(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            href = self.item(row, 0).text()
            self.set_media_status(href, 1)

            for media in self.queue_media_list:
                if media.url == href and media.status != 1:
                    media.status = 1
                    self.state_service.save_download_queue_media(self.queue_media_list)
                    download_video_thread = Thread(target=self.download_video, daemon=True, args=[media])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()

    def set_media_status(self, url, status, status_name):
        i = 0
        for media in self.queue_media_list:
            if media.url == url:
                media.status = status
                self.state_service.save_download_queue_media(self.queue_media_list)
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
            self.state_service.save_download_queue_media(self.queue_media_list)
            if url in self.download_thread_dict:
                self.download_thread_dict[url].join()
                self.download_thread_dict[url] = None
