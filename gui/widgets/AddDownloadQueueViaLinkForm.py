import traceback

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

    def __init__(self, parent, format, quality, remove_files_after_upload):

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
        self.remove_files_after_upload = remove_files_after_upload
        self.event_service = EventService()

    def choose(self):
        accounts = self.state_service.get_accounts_by_hosting(self.hosting_combo_box.currentText())

        if len(accounts) == 0 and Hosting[self.hosting_combo_box.currentText()].value[1]:
            msg = QMessageBox()
            msg.setText(get_str('need_authorize'))
            msg.exec_()
            return
        elif len(accounts) != 0:
            form = ChooseAccountForm(parent=self.parentWidget(),
                                     accounts=accounts)
            form.exec_()
            self.account = form.account
            if form.account is None and Hosting[self.hosting_combo_box.currentText()].value[1]:
                return

        self.hosting = self.hosting_combo_box.itemData(self.hosting_combo_box.currentIndex())

        form = ChooseLinkForm(parent=self.parentWidget(), hosting=self.hosting_combo_box.currentText())
        form.exec_()

        if form.passed is False:
            return

        self.link = form.link_edit.text()
        if self.format != 3:
            form = UploadAfterDownloadForm(self, need_interval=False)
            form.exec_()

            if form.passed is False:
                self.close()
                return

            self.upload_on = form.upload_flag
            self.upload_targets = list()

            if self.upload_on:
                video_info = self.hosting.value[0].get_video_info(self.link,
                                                                  self.video_quality,
                                                                  self.account)
                # Если необходимо выгружать видео после загрузки, проводим валидацию
                for upload_target in form.upload_targets:
                    upload_hosting = Hosting[upload_target['hosting']]
                    try:
                        upload_hosting.value[0].validate_video_info_for_uploading(title=video_info['title'],
                                                                                  description=video_info[
                                                                                      'description'],
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
                        self.upload_on = False
                    except FileSizeException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_size")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.upload_on = False
                    except FileFormatException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_format")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.upload_on = False
                    except NameIsTooLongException:
                        self.title = video_info['title']
                        while len(self.title) > self.upload_hosting.value[0].title_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=self,
                                               label=f'{get_str("too_long_title")}{str(upload_hosting.value[0].title_size_restriction)}',
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
                    self.queue_media_service.add_to_the_upload_queue(
                        UploadQueueMedia(video_dir=get_str('upload_yet'),
                                         hosting=target['hosting'],
                                         status=5,
                                         account=self.state_service.get_account_by_hosting_and_login(
                                             target['hosting'],
                                             target['login']),
                                         remove_files_after_upload=self.remove_files_after_upload))

        self.passed = True
        self.close()
