import traceback
import uuid

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout)

from gui.widgets.TypeStrForm import TypeStrForm
from gui.widgets.UploadAfterDownloadForm import UploadAfterDownloadForm
from model.Event import Event
from model.Hosting import Hosting
from model.UploadQueueMedia import UploadQueueMedia
from service.EventService import EventService
from service.LocalizationService import *
from gui.widgets.ChooseAccountForm import ChooseAccountForm
from gui.widgets.ChooseLinkForm import ChooseLinkForm
from service.LoggingService import log_error
from service.QueueMediaService import QueueMediaService
from service.videohosting_service.exception.DescriptionIsTooLongException import DescriptionIsTooLongException
from service.videohosting_service.exception.FileFormatException import FileFormatException
from service.videohosting_service.exception.FileSizeException import FileSizeException
from service.videohosting_service.exception.NameIsTooLongException import NameIsTooLongException
from service.videohosting_service.exception.VideoDurationException import VideoDurationException


class AddDownloadQueueViaLinkForm(QDialog):
    video_quality = None
    account = None
    hosting = None
    link = None
    passed = False
    format = None
    upload_on = False
    upload_targets = None
    title = None
    description = None
    video_size = None
    id = None

    def __init__(self, parent, format, quality, extension, remove_files_after_upload, manual_settings,
                 video_quality_str, audio_quality_str, video_bitrate, audio_bitrate, audio_sampling_rate, fps):

        super().__init__(parent)
        self.setWindowTitle(get_str('adding_video_via_url'))
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(f'<font size="4"> {get_str("videohosting")} </font>')
        self.hosting_combo_box = QComboBox()

        for hosting in Hosting:
            self.hosting_combo_box.addItem(hosting.name, hosting)

        self.hosting_combo_box.setCurrentIndex(0)

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.hosting_combo_box, 0, 1)

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose)
        layout.addWidget(button_choose, 2, 0, 1, 2)
        layout.setRowMinimumHeight(4, 75)

        self.setLayout(layout)
        self.state_service = StateService()
        self.queue_media_service = QueueMediaService()
        self.format = format
        self.video_quality = quality
        self.video_extension = extension
        self.remove_files_after_upload = remove_files_after_upload
        self.video_quality_str = video_quality_str
        self.audio_quality_str = audio_quality_str
        self.video_bitrate = video_bitrate
        self.audio_bitrate = audio_bitrate
        self.audio_sampling_rate = audio_sampling_rate
        self.fps = fps
        self.manual_settings = manual_settings
        self.event_service = EventService()

    def choose(self):
        accounts = self.state_service.get_accounts_by_hosting(self.hosting_combo_box.currentText())

        if len(accounts) == 0 and Hosting[self.hosting_combo_box.currentText()].value[1]:
            msg = QMessageBox()
            msg.setText(get_str('need_authorize'))
            msg.exec_()
            return
        elif len(accounts) != 0 and Hosting[self.hosting_combo_box.currentText()].value[1]:
            choose_account_form = ChooseAccountForm(self, accounts)
            choose_account_form.exec_()

            if choose_account_form.account is None:
                return

            self.account = choose_account_form.account
        elif len(accounts) != 0:
            self.account = accounts[0]

        self.hosting = self.hosting_combo_box.itemData(self.hosting_combo_box.currentIndex())

        form = ChooseLinkForm(parent=self.parentWidget(), hosting=self.hosting_combo_box.currentText())
        form.exec_()

        if form.passed is False:
            return

        self.video_size = get_str('no_info')
        self.link = form.link_edit.text()

        if self.format != 3:
            try:
                video_info = self.hosting.value[0].get_video_info(self.link,
                                                                  video_quality=self.video_quality,
                                                                  video_extension=self.video_extension,
                                                                  fps=self.fps,
                                                                  audio_bitrate=self.audio_bitrate,
                                                                  video_bitrate=self.video_bitrate,
                                                                  audio_sampling_rate=self.audio_sampling_rate,
                                                                  audio_quality_str=self.audio_quality_str,
                                                                  video_quality_str=self.video_quality_str,
                                                                  manual_settings=self.manual_settings,
                                                                  account=self.account)
                self.title = video_info['title']
                if self.title is None:
                    self.title = ''
                self.description = video_info['description']
            except:
                log_error(traceback.format_exc())
                self.event_service.add_event(
                    Event(f'{get_str("technical_error")}: {self.link}'))
                msg = QMessageBox()
                msg.setText(get_str('technical_error'))
                msg.exec_()
                return

            if video_info is None:
                self.video_size = get_str('no_info')
            else:
                self.video_size = video_info['filesize']

            form = UploadAfterDownloadForm(self, need_interval=False, video_size=self.video_size)
            form.exec_()

            if form.passed is False:
                self.close()
                return

            self.upload_on = form.upload_flag
            self.upload_targets = list()

            if self.upload_on:
                # Если необходимо выгружать видео после загрузки, проводим валидацию
                for upload_target in form.upload_targets:
                    upload_target['id'] = uuid.uuid4()
                    upload_hosting = Hosting[upload_target['hosting']]
                    try:
                        upload_target['error'] = False
                        upload_hosting.value[0].validate_video_info_for_uploading(title=self.title,
                                                                                  description=self.description,
                                                                                  duration=video_info[
                                                                                      'duration'],
                                                                                  filesize=video_info[
                                                                                      'filesize'],
                                                                                  ext=video_info['ext'])
                    except VideoDurationException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_duration")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item('upload_yet', upload_target, f'{get_str("bad_file_duration")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}')
                        upload_target['error'] = True
                    except FileSizeException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_size")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item('upload_yet', upload_target, f'{get_str("bad_file_size")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}')
                        upload_target['error'] = True
                    except FileFormatException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_format")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item('upload_yet', upload_target, f'{get_str("bad_file_format")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}')
                        upload_target['error'] = True
                    except NameIsTooLongException:
                        while (upload_hosting.value[0].title_size_restriction is not None and
                               len(self.title) > upload_hosting.value[0].title_size_restriction) or \
                                (upload_hosting.value[0].min_title_size is not None and
                                 len(self.title) < upload_hosting.value[0].min_title_size):
                            log_error(traceback.format_exc())
                            if upload_hosting.value[0].title_size_restriction is not None:
                                label = f'{get_str("bad_title")} ({str(upload_hosting.value[0].min_title_size)} >= {get_str("name")} < {str(upload_hosting.value[0].title_size_restriction)}'
                            else:
                                label = f'{get_str("bad_title")} ({str(upload_hosting.value[0].min_title_size)} >= {get_str("name")}'
                            form = TypeStrForm(parent=self,
                                               label=label,
                                               current_text=self.title)
                            form.exec_()
                            self.title = form.str

                    except DescriptionIsTooLongException:
                        self.description = video_info['description']
                        while len(self.description) > self.upload_hosting.value[0].description_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=self,
                                               label=f'{get_str("too_long_description")}{str(upload_hosting.value[0].description_size_restriction)}',
                                               current_text=self.description)
                            form.exec_()
                            self.description = form.str
                    self.upload_targets.append(upload_target)
                                
                for target in self.upload_targets:
                    if 'error' not in target or target['error'] is False:
                        account = self.state_service.get_account_by_hosting_and_login(target['hosting'], target['login'])
                        self.queue_media_service.add_to_the_upload_queue(
                            UploadQueueMedia(media_id=str(target['id']),
                                             video_dir='upload_yet',
                                             hosting=target['hosting'],
                                             status=5,
                                             account=account,
                                             destination=account.url,
                                             remove_files_after_upload=self.remove_files_after_upload))

        self.passed = True
        self.close()

    def add_error_upload_item(self, link, target, error: str):
        self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(target['id']),
                                                                          video_dir=link,
                                                                          hosting=target['hosting'],
                                                                          status=3,
                                                                          account=self.state_service.get_account_by_hosting_and_login(
                                                                              target['hosting'],
                                                                              target['login']),
                                                                          destination=target[
                                                                              'upload_target'],
                                                                          upload_date=None,
                                                                          remove_files_after_upload=False,
                                                                          error_name=error))
