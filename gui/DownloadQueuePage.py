import asyncio
import uuid
from datetime import datetime
from functools import partial
from threading import Lock

from youtube_dl import DownloadError
from yt_dlp import DownloadError
from PyQt5 import QtCore, QtWidgets
from gui.widgets.AddUploadQueueByUploadedMediaForm import AddUploadQueueByUploadedMediaForm
from gui.widgets.ShowErrorDialog import ShowErrorDialog
from model.Event import Event
from service.EventService import EventService
from service.MailService import MailService
from service.QueueMediaService import QueueMediaService
from model.Hosting import Hosting
from model.UploadQueueMedia import UploadQueueMedia
import kthread
from PyQt5.QtCore import QTimer
from service.LoggingService import *
from service.LocalizationService import *
import traceback
import time

from service.videohosting_service.exception.NoFreeSpaceException import NoFreeSpaceException


class DownloadQueuePageWidget(QtWidgets.QTableWidget):
    state_service = StateService()
    event_service = EventService()
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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.download_media_by_download_strategy)
        self.timer.start(3_000)

        self.update_load_items_timer = QTimer(self)
        self.update_load_items_timer.timeout.connect(self.update_load_items)
        self.update_load_items_timer.start(3_000)

        self.strategy = self.settings.download_strategy


        self.lock = Lock()
        self.horizontalHeader().sectionResized.connect(self.section_resized)

    def on_add(self):
        button = self.sender()
        if button:
            form = AddUploadQueueByUploadedMediaForm(self, self.queue_media_list[self.indexAt(button.pos()).row()].video_dir)
            form.exec_()

            if form.passed is True and form.result is not None:
                for target in form.result[4]:
                    if 'error' not in target or target['error'] is False:
                        self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(uuid.uuid4()),
                                                                                          video_dir=form.result[0],
                                                                                          hosting=target['hosting'],
                                                                                          status=0,
                                                                                          account=self.state_service.get_account_by_hosting_and_login(
                                                                                              target['hosting'],
                                                                                              target['login'],
                                                                                              target['upload_target']
                                                                                          ),
                                                                                          destination=target[
                                                                                              'upload_target'],
                                                                                          upload_date=form.result[3],
                                                                                          title=target['title'],
                                                                                          description=target['description'],
                                                                                          remove_files_after_upload=False))

    def download_media_by_download_strategy(self):
        for media in self.queue_media_list:
            if media.status == 0 and media.load_date is not None:
                if media.download_strategy == 1:
                    if len(self.download_thread_dict) == 0:
                        self.add_to_download_list(media)
                elif media.download_strategy == 2:
                    if len(self.download_thread_dict) < media.pack_count:
                        self.add_to_download_list(media)

    def add_to_download_list(self, media):
        if datetime.now() > media.load_date:
            event_loop = None

            if Hosting[media.hosting].value[0].is_async():
                event_loop = asyncio.new_event_loop()

            download_video_thread = kthread.KThread(target=self.download_video, daemon=True,
                                                    args=[media, event_loop])

            self.download_thread_dict[media.id] = download_video_thread
            download_video_thread.start()

    def update_load_items(self):
        for queue_media in self.queue_media_list:
            if queue_media.status == 0:
                if queue_media.load_date is None and queue_media.wait_for is None:
                    queue_media.load_date = datetime.now()
                elif queue_media.load_date is None and queue_media.load_in is not None:
                    media = self.get_media_by_id(queue_media.wait_for)
                    if media is not None:
                        if media.status == 2:
                            queue_media.load_date = datetime.now() + queue_media.load_in
                    else:
                        queue_media.load_date = datetime.now() + queue_media.load_in

    def download_video(self, media, event_loop):
        try:
            time.sleep(1)
            if media.status != 1:
                self.set_media_status(media.id, 1)

            if event_loop is not None:
                asyncio.set_event_loop(event_loop)

            video_dir = Hosting[media.hosting].value[0].download_video(
                url=media.url,
                account=media.account,
                hosting=media.hosting,
                table_item=self.cellWidget(self.get_row_index(media.id), 1),
                download_dir=media.download_dir,
                format=media.format,
                video_quality=media.video_quality,
                video_extension=media.video_extension,
                manual_settings=media.manual_settings,
                audio_quality_str=media.audio_quality_str,
                video_quality_str=media.video_quality_str,
                audio_bitrate=media.audio_bitrate,
                video_bitrate=media.video_bitrate,
                audio_sampling_rate=media.audio_sampling_rate,
                fps=media.fps)

            hash = str(uuid.uuid4())
            if media.upload_after_download:
                old_dir = video_dir
                video_dir = video_dir.replace(os.path.splitext(video_dir)[0], os.path.splitext(video_dir)[0] + f'_{hash}')
                os.renames(old_dir, video_dir)
                os.renames(os.path.splitext(old_dir)[0] + '.info.json',
                           (os.path.splitext(old_dir)[0] + '.info.json').replace(os.path.splitext(old_dir)[0], os.path.splitext(old_dir)[0] + f'_{hash}'))

            self.state_service.add_loaded_video_to_the_history(media.url, media.video_quality, media.video_extension)

            media.video_dir = video_dir
            if media.upload_after_download:
                for upload_target in media.upload_targets:
                    if upload_target['error'] is False:
                        status = 0
                    else:
                        status = 6

                    self.queue_media_service.replace_to_the_upload_queue(UploadQueueMedia(media_id=str(upload_target['id']),
                                                                                          video_dir=video_dir,
                                                                                          hash=hash,
                                                                                          hosting=upload_target[
                                                                                              'hosting'],
                                                                                          status=status,
                                                                                          account=self.state_service.get_account_by_hosting_and_login(
                                                                                              upload_target['hosting'],
                                                                                              upload_target['login'],
                                                                                              upload_target['upload_target']),
                                                                                          destination=upload_target[
                                                                                              'upload_target'],
                                                                                          upload_in=media.upload_in,
                                                                                          remove_files_after_upload=media.remove_files_after_upload,
                                                                                          title=upload_target['title'],
                                                                                          description=upload_target['description']))
        except SystemExit:
            self.download_thread_dict.pop(media.id)
            self.set_media_status(media.id, 4)
            self.download_thread_dict.pop(media.id)
            return
        except NoFreeSpaceException:
            self.download_thread_dict.pop(media.id)
            log_error(traceback.format_exc())
            self.set_media_status(media.id, 3, status_name='no_free_space')
            return
        except DownloadError as er:
            self.download_thread_dict.pop(media.id)
            log_error(traceback.format_exc())
            if er.args[0].__contains__('Unable to download video JSON'):
                self.set_media_status(media.id, 3, status_name='bad_internet_connection')
            else:
                self.set_media_status(media.id, 3, status_name='technical_error')
            if self.settings.send_crash_notifications is True:
                MailService().send_log()
            return
        except Exception:
            self.download_thread_dict.pop(media.id)
            log_error(traceback.format_exc())
            self.set_media_status(media.id, 3)
            if self.settings.send_crash_notifications is True:
                MailService().send_log()
            return

        self.event_service.add_event(Event(f'{get_str("event_downloaded")} {media.id}'))
        self.set_media_status(media.id, 2)
        self.download_thread_dict.pop(media.id)

    def get_media_by_id(self, id):
        for media in self.queue_media_list:
            if media.id == id:
                return media
        return None

    def update_queue_media(self):
        last_added_queue_media = self.queue_media_service.get_last_added_download_queue_media()
        for queue_media in last_added_queue_media:
            self.insert_queue_media(queue_media)

    def insert_queue_media(self, queue_media):
        self.insertRow(self.rowCount())
        input_position = self.rowCount() - 1

        item1 = QtWidgets.QTableWidgetItem(queue_media.url)
        item1.setData(11, queue_media.id)

        action_button = QtWidgets.QPushButton(self)
        if queue_media.status == 0 or queue_media.status == 4:
            item2 = QtWidgets.QPushButton(get_str('stopped'))
            item2.clicked.connect(self.do_nothing)
            action_button.setText(get_str('start'))
            action_button.clicked.connect(self.on_start_download)
        elif queue_media.status == 1:
            if self.settings.enable_autostart:
                item2 = QtWidgets.QPushButton(get_str('process'))
                item2.clicked.connect(self.do_nothing)
                action_button.setText(get_str('stop'))
                action_button.clicked.connect(self.on_stop_download)

                if queue_media.id not in self.download_thread_dict.keys():
                    event_loop = None

                    if Hosting[queue_media.hosting].value[0].is_async():
                        event_loop = asyncio.new_event_loop()

                    time.sleep(1)

                    download_video_thread = kthread.KThread(target=self.download_video, daemon=True,
                                                            args=[queue_media, event_loop])
                    self.download_thread_dict[queue_media.id] = download_video_thread
                    download_video_thread.start()
            else:
                item2 = QtWidgets.QPushButton(get_str('stopped'))
                item2.clicked.connect(self.do_nothing)
                action_button.setText(get_str('start'))
                action_button.clicked.connect(self.on_start_download)
                queue_media.status = 4
                state_service.save_download_queue_media(self.queue_media_list)

        elif queue_media.status == 2:
            item2 = QtWidgets.QPushButton(get_str('end'))
            item2.clicked.connect(self.do_nothing)
            action_button.setText(get_str('add_video_for_uploading'))
            action_button.clicked.connect(self.on_add)
        else:
            item2 = QtWidgets.QPushButton(get_str('error'))
            item2.clicked.connect(partial(self.show_error, get_str(queue_media.status_name)))
            action_button.setText(get_str('retry'))
            action_button.clicked.connect(self.on_start_download)

        action_button.clicked.connect(self.do_nothing)
        self.setCellWidget(input_position, 2, action_button)

        delete_button = QtWidgets.QPushButton(self)
        delete_button.setText('-')
        self.setCellWidget(input_position, 3, delete_button)

        delete_button.clicked.connect(self.on_delete_row)

        self.setItem(input_position, 0, item1)
        self.setCellWidget(input_position, 1, item2)

    def set_media_status(self, media_id, status, status_name=None):
        i = 0
        self.lock.acquire()
        for media in self.queue_media_list:
            if media.id == media_id:
                media.status = status
                self.state_service.save_download_queue_media(self.queue_media_list)

                if status == 0 or status == 4:
                    self.cellWidget(i, 1).setText(get_str('stopped'))
                    self.cellWidget(i, 1).clicked.disconnect()
                    self.cellWidget(i, 1).clicked.connect(self.do_nothing)

                    self.cellWidget(i, 2).setText(get_str('start'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_start_download)
                elif status == 1:
                    self.cellWidget(i, 1).setText(get_str('process'))
                    self.cellWidget(i, 1).clicked.disconnect()
                    self.cellWidget(i, 1).clicked.connect(self.do_nothing)

                    self.cellWidget(i, 2).setText(get_str('stop'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_stop_download)
                elif status == 2:
                    self.cellWidget(i, 1).setText(get_str('end'))
                    self.cellWidget(i, 1).clicked.disconnect()
                    self.cellWidget(i, 1).clicked.connect(self.do_nothing)

                    self.cellWidget(i, 2).setText(get_str('add_video_for_uploading'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_add)
                elif status == 3:
                    self.cellWidget(i, 1).setText(get_str('error'))
                    self.cellWidget(i, 1).clicked.disconnect()

                    if status_name is None:
                        self.cellWidget(i, 1).setText(get_str('error'))
                        media.status_name = 'technical_error'
                        self.cellWidget(i, 1).clicked.connect(partial(self.show_error, get_str('technical_error')))
                    else:
                        self.cellWidget(i, 1).setText(get_str('error'))
                        media.status_name = status_name
                        self.cellWidget(i, 1).clicked.connect(partial(self.show_error, get_str(status_name)))

                    self.cellWidget(i, 2).setText(get_str('retry'))
                    self.cellWidget(i, 2).clicked.disconnect()
                    self.cellWidget(i, 2).clicked.connect(self.on_start_download)
                break
            i += 1

        self.state_service.save_download_queue_media(self.queue_media_list)
        self.lock.release()

    def do_nothing(self):
        pass

    def get_row_index(self, media_id):
        i = 0
        for media in self.queue_media_list:
            if media.id == media_id:
                return i
            i += 1

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            pos = self.horizontalScrollBar().sliderPosition()
            self.removeRow(row)
            media_id = self.queue_media_list.pop(row).id
            self.state_service.save_download_queue_media(self.queue_media_list)

            if media_id in self.download_thread_dict:
                if self.download_thread_dict[media_id] is not None and self.download_thread_dict[media_id].is_alive():
                    self.download_thread_dict[media_id].terminate()
                self.download_thread_dict[media_id] = None
            self.horizontalScrollBar().setSliderPosition(pos)

    # Функции для кнопок остановить и начать
    def on_stop_download(self):
        button = self.sender()
        if button:
            time.sleep(0.2)
            row = self.indexAt(button.pos()).row()
            media_id = self.item(row, 0).data(11)
            self.set_media_status(media_id, 4)

            if media_id in self.download_thread_dict:
                if self.download_thread_dict[media_id] is not None and self.download_thread_dict[media_id].is_alive():
                    self.download_thread_dict[media_id].terminate()
                self.download_thread_dict[media_id] = None

    def show_error(self, status_name):
        dialog = ShowErrorDialog(self, status_name)
        dialog.exec_()

    def on_start_download(self):
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

                    download_video_thread = kthread.KThread(target=self.download_video, daemon=True,
                                                            args=[media, event_loop])

                    self.download_thread_dict[media.id] = download_video_thread
                    download_video_thread.start()

    change = True

    def section_resized(self, index, width):
        if self.change:
            coef_x = self.parent().width() / 950
            self.state_service.save_column_row('download', index, int(width / coef_x))

    def resizeEvent(self, event):
        self.change = False
        coef_x = self.parent().width() / 950

        if self.state_service.column_row('download', 0) is None or self.state_service.column_row('download', 1) is None or self.state_service.column_row('download', 2) is None or self.state_service.column_row('download', 3) is None:
            column_width = int(950 / 4)

            if self.state_service.column_row('download', 0) is None:
                self.state_service.save_column_row('download', 0, column_width)
            if self.state_service.column_row('download', 1) is None:
                self.state_service.save_column_row('download', 1, column_width)
            if self.state_service.column_row('download', 2) is None:
                self.state_service.save_column_row('download', 2, column_width)
            if self.state_service.column_row('download', 3) is None:
                self.state_service.save_column_row('download', 3, column_width)

        width_0 = int(self.state_service.column_row('download', 0) * coef_x)
        width_1 = int(self.state_service.column_row('download', 1) * coef_x)
        width_2 = int(self.state_service.column_row('download', 2) * coef_x)
        width_3 = int(self.state_service.column_row('download', 3) * coef_x)

        self.setColumnWidth(0, width_0)
        self.setColumnWidth(1, width_1)
        self.setColumnWidth(2, width_2)
        self.setColumnWidth(3, width_3)

        self.change = True

        return super(DownloadQueuePageWidget, self).resizeEvent(event)
