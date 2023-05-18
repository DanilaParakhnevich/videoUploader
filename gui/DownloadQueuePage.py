import asyncio

from PyQt5 import QtCore, QtWidgets

from service.QueueMediaService import QueueMediaService
from model.Hosting import Hosting
from model.UploadQueueMedia import UploadQueueMedia
from model.LoadQueuedMedia import LoadQueuedMedia
from gui.widgets.AddDownloadQueueViaLinkForm import AddDownloadQueueViaLinkForm
from gui.widgets.LoadingButton import AnimatedButton
import kthread
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

        horizontal_layout = QtWidgets.QHBoxLayout(self)
        horizontal_layout.setObjectName("horizontal_layout")

        self.add_button = AnimatedButton(central_widget)
        self.add_button.setObjectName("add_button")
        self.add_button.setText(get_str('add_download_single_video_by_link'))
        horizontal_layout.addWidget(self.add_button)
        horizontal_layout.setAlignment(QtCore.Qt.AlignBottom)

        self.add_button.clicked.connect(self.on_add)

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

                    event_loop = None

                    if Hosting[media.hosting].value[0].is_async():
                        event_loop = asyncio.new_event_loop()

                    download_video_thread = kthread.KThread(target=self.download_video, daemon=True,
                                                            args=[media, event_loop])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()

    def downloading_parallel_hook(self):
        if len(self.download_thread_dict) < self.settings.pack_count:
            for media in self.queue_media_list:
                if len(self.download_thread_dict) < self.settings.pack_count and media.status == 0:

                    event_loop = None

                    if Hosting[media.hosting].value[0].is_async():
                        event_loop = asyncio.new_event_loop()

                    download_video_thread = kthread.KThread(target=self.download_video, daemon=True,
                                                            args=[media, event_loop])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()

    def download_video(self, media, event_loop):
        try:
            time.sleep(1)
            if media.status != 1:
                self.set_media_status(media.url, 1)

            if event_loop is not None:
                asyncio.set_event_loop(event_loop)

            video_dir = Hosting[media.hosting].value[0].download_video(
                url=media.url,
                account=media.account,
                hosting=media.hosting,
                table_item=self.item(self.get_row_index(media.url), 1),
                format=media.format,
                video_quality=media.video_quality)
            if media.upload_after_download:
                for upload_target in media.upload_targets:
                    self.queue_media_service.replace_to_the_upload_queue(UploadQueueMedia(video_dir=video_dir,
                                                                                      hosting=upload_target['hosting'],
                                                                                      status=0,
                                                                                      account=self.state_service.get_account_by_hosting_and_login(upload_target['hosting'], upload_target['login']),
                                                                                      destination=upload_target['upload_target'],
                                                                                      upload_date=media.upload_date,
                                                                                      remove_files_after_upload=media.remove_files_after_upload,
                                                                                      title=media.title,
                                                                                      description=media.description))
        except SystemExit:
            self.set_media_status(media.url, 0)
            self.download_thread_dict.pop(media.url)
            return
        except Exception:
            log_error(traceback.format_exc())
            self.set_media_status(media.url, 3)
            return

        self.set_media_status(media.url, 2)
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
            item2 = QtWidgets.QTableWidgetItem(get_str('stopped'))
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_download)
        elif queue_media.status == 1:
            item2 = QtWidgets.QTableWidgetItem(get_str('process'))
            action_button.setText(get_str('stop'))
            action_button.clicked.connect(self.on_stop_download)

            if queue_media.url not in self.download_thread_dict.keys():
                event_loop = None

                if Hosting[queue_media.hosting].value[0].is_async():
                    event_loop = asyncio.new_event_loop()

                time.sleep(1)

                download_video_thread = kthread.KThread(target=self.download_video, daemon=True,
                                                        args=[queue_media, event_loop])
                self.download_thread_dict[queue_media.url] = download_video_thread
                download_video_thread.start()

        elif queue_media.status == 2:
            item2 = QtWidgets.QTableWidgetItem(get_str('end'))
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_download)
        else:
            item2 = QtWidgets.QTableWidgetItem(get_str('error'))
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_download)

        self.setCellWidget(input_position, 2, action_button)

        delete_button = QtWidgets.QPushButton(self)
        delete_button.setText('-')
        self.setCellWidget(input_position, 3, delete_button)

        delete_button.clicked.connect(self.on_delete_row)

        self.setItem(input_position, 0, item1)
        self.setItem(input_position, 1, item2)

    def set_media_status(self, url, status):
        i = 0
        time.sleep(0.2)
        for media in self.queue_media_list:
            if media.url == url:
                media.status = status
                self.state_service.save_download_queue_media(self.queue_media_list)

                if status == 0:
                    self.item(i, 1).setText(get_str('stopped'))
                    self.cellWidget(i, 2).setText(get_str('start'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_start_download)
                elif status == 1:
                    self.item(i, 1).setText(get_str('process'))
                    self.cellWidget(i, 2).setText(get_str('stop'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_stop_download)
                elif status == 2:
                    self.item(i, 1).setText(get_str('end'))
                    self.cellWidget(i, 2).setText(get_str('start'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_start_download)
                elif status == 3:
                    self.item(i, 1).setText(get_str('error'))
                    self.cellWidget(i, 2).setText(get_str('start'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_start_download)
                break
            i += 1

    def get_row_index(self, url):
        i = 0
        for media in self.queue_media_list:
            if media.url == url:
                return i
            i += 1

    def on_add(self):
        form = AddDownloadQueueViaLinkForm(self)
        form.exec_()

        if form.passed is True:
            queue_media = LoadQueuedMedia(url=form.link,
                                          hosting=form.hosting.name,
                                          status=0,
                                          upload_after_download=form.upload_on,
                                          account=form.account,
                                          format=form.format,
                                          video_quality=form.video_quality,
                                          remove_files_after_upload=form.remove_files_after_upload.isChecked(),
                                          upload_destination=form.upload_target,
                                          upload_account=form.upload_account,
                                          title=form.title,
                                          description=form.description)

            self.queue_media_list.append(queue_media)
            self.insert_queue_media(queue_media)

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            self.removeRow(row)
            url = self.queue_media_list.pop(row).url
            self.state_service.save_download_queue_media(self.queue_media_list)

            if url in self.download_thread_dict:
                if self.download_thread_dict[url] is not None and self.download_thread_dict[url].is_alive():
                    self.download_thread_dict[url].terminate()
                self.download_thread_dict[url] = None

    # Функции для кнопок остановить и начать
    def on_stop_download(self):
        button = self.sender()
        if button:
            time.sleep(0.2)
            row = self.indexAt(button.pos()).row()
            url = self.item(row, 0).text()
            self.set_media_status(url, 0)

            if url in self.download_thread_dict:
                if self.download_thread_dict[url] is not None and self.download_thread_dict[url].is_alive():
                    self.download_thread_dict[url].terminate()
                self.download_thread_dict[url] = None

    def on_start_download(self):
        button = self.sender()
        if button:
            time.sleep(0.2)
            row = self.indexAt(button.pos()).row()
            url = self.item(row, 0).text()
            self.set_media_status(url, 1)

            for media in self.queue_media_list:
                if media.url == url:
                    event_loop = None

                    if Hosting[media.hosting].value[0].is_async():
                        event_loop = asyncio.new_event_loop()

                    download_video_thread = kthread.KThread(target=self.download_video, daemon=True,
                                                            args=[media, event_loop])

                    self.download_thread_dict[media.url] = download_video_thread
                    download_video_thread.start()
