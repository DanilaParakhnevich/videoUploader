import traceback
import uuid
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout)
from dateutil.relativedelta import relativedelta

from gui.widgets.ChooseAccountsForUploadingForm import ChooseAccountsForUploadingForm
from model.Event import Event
from model.Hosting import Hosting
from model.UploadQueueMedia import UploadQueueMedia
from service.EventService import EventService
from service.LocalizationService import *
from gui.widgets.TypeStrForm import TypeStrForm
import os

from service.LoggingService import log_error
from service.QueueMediaService import QueueMediaService
from service.videohosting_service.exception.DescriptionIsTooLongException import DescriptionIsTooLongException
from service.videohosting_service.exception.FileFormatException import FileFormatException
from service.videohosting_service.exception.FileSizeException import FileSizeException
from service.videohosting_service.exception.NameIsTooLongException import NameIsTooLongException
from service.videohosting_service.exception.VideoDurationException import VideoDurationException


class AddUploadQueueByUploadedMediaForm(QDialog):

    def __init__(self, parent, dir):

        super().__init__(parent)
        self.setWindowTitle(get_str('adding_video_by_uploaded_media'))
        self.setFixedSize(500, 120)

        layout = QGridLayout()

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose)
        layout.addWidget(button_choose, 0, 0)
        layout.setRowMinimumHeight(3, 75)

        self.upload_targets = list()
        self.destination = None
        self.directory = None
        self.video_info = None
        self.passed = False
        self.dir = dir

        self.setLayout(layout)
        self.state_service = StateService()
        self.event_service = EventService()
        self.queue_media_service = QueueMediaService()

    def choose(self):
        choose_accounts_for_uploading_form = ChooseAccountsForUploadingForm(self)
        choose_accounts_for_uploading_form.exec_()

        if choose_accounts_for_uploading_form.passed is False or len(choose_accounts_for_uploading_form.accounts) == 0:
            self.close()
            return

        accounts = choose_accounts_for_uploading_form.accounts
        for account in accounts:
            self.upload_targets.append({
                'login': account.login,
                'hosting': account.hosting,
                'upload_target': account.url})

        self.video_info = list()

        self.result = None

        if os.path.exists(self.dir) is False:
            for upload_target in self.upload_targets:
                self.event_service.add_event(Event(f'{get_str("video_not_exists")}: {self.dir}'))
                self.add_error_upload_item(self.dir, upload_target, f'{get_str("video_not_exists")}: {self.dir}')
            self.passed = True
            self.close()
            return

        handle_result = self.handle_file(self.dir)
        if handle_result is not False:
            self.result = handle_result

        self.passed = True
        self.close()

    def handle_file(self, file_dir):
        title = None
        description = None
        upload = False
        upload_targets = list()

        try:
            f = open(os.path.splitext(file_dir)[0] + '.info.json', 'r', encoding='utf-8')
            data = json.load(f)

            title = data['title']

            if 'description' in data:
                description = data['description']

        except:
            log_error(f'{os.path.splitext(file_dir)[0]} - .info.json не найден')

        for target in self.upload_targets:
            try:
                target['title'] = title
                target['description'] = description
                Hosting[target['hosting']].value[0].validate_video_info_for_uploading(video_dir=file_dir)
            except VideoDurationException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_duration")}{file_dir}'))
                self.add_error_upload_item(file_dir, target, f'{get_str("bad_file_duration")}{file_dir}')
                continue
            except FileSizeException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_size")}{file_dir}'))
                self.add_error_upload_item(file_dir, target, f'{get_str("bad_file_size")}{file_dir}')
                continue
            except FileFormatException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_format")}{file_dir}'))
                self.add_error_upload_item(file_dir, target, f'{get_str("bad_file_format")}{file_dir}')
                continue

            try:
                if target['title'] is None:
                    form = TypeStrForm(parent=self, label=f'{get_str("input_title")}: {file_dir}')
                    form.exec_()

                    target['title'] = form.str

                Hosting[target['hosting']].value[0].validate_video_info_for_uploading(title=target['title'])
            except NameIsTooLongException:
                while (Hosting[target['hosting']].value[0].title_size_restriction is not None and \
                        len(target['title']) > Hosting[target['hosting']].value[0].title_size_restriction) or \
                        (Hosting[target['hosting']].value[0].min_title_size is not None and \
                        len(target['title']) < Hosting[target['hosting']].value[0].min_title_size):
                    log_error(traceback.format_exc())
                    if Hosting[target['hosting']].value[0].title_size_restriction is not None:
                        label = f'{get_str("bad_title")} ({str(Hosting[target["hosting"]].value[0].min_title_size)} <= {get_str("name")} > {str(Hosting[target["hosting"]].value[0].title_size_restriction)})'
                    else:
                        label = f'{get_str("bad_title")} ({str(Hosting[target["hosting"]].value[0].min_title_size)} <= {get_str("name")})'
                    form = TypeStrForm(parent=self,
                                       label=label,
                                       current_text=target['title'])
                    form.exec_()
                    target['title'] = form.str

            if Hosting[target['hosting']].value[0].description_size_restriction is not None:
                try:
                    if target['description'] is None:
                        form = TypeStrForm(parent=self, label=f'{get_str("input_description")}: {file_dir}')
                        form.exec_()

                        target['description'] = form.str

                    Hosting[target['hosting']].value[0].validate_video_info_for_uploading(description=target['description'])
                except DescriptionIsTooLongException:
                    while len(target['description']) > Hosting[target['hosting']].value[0].description_size_restriction:
                        log_error(traceback.format_exc())
                        form = TypeStrForm(parent=self,
                                           label=f'{get_str("too_long_description")}{str(Hosting[target["hosting"]].value[0].description_size_restriction)}',
                                           current_text=target['description'])
                        form.exec_()
                        target['description'] = form.str

            upload_targets.append(target)
            upload = True
        if upload:
            return list([file_dir, title, description, datetime.now(), upload_targets])
        else:
            return False

    def add_error_upload_item(self, file_dir, target, error: str):
        self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(uuid.uuid4()),
                                                                          video_dir=file_dir,
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