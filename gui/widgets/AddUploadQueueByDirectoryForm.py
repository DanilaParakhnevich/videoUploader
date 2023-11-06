import traceback
import uuid
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout)
from dateutil.relativedelta import relativedelta

from gui.widgets.ChooseAccountsForUploadingForm import ChooseAccountsForUploadingForm
from model.Event import Event
from model.Hosting import Hosting
from model.UploadQueueMedia import UploadQueueMedia
from service.EventService import EventService
from service.LocalizationService import *
from gui.widgets.ChooseDirForm import ChooseDirForm
from gui.widgets.DirOrFileForm import DirOrFileForm
from gui.widgets.TypeStrForm import TypeStrForm
from gui.widgets.ChooseIntervalsForm import ChooseIntervalForm
import os

from service.LoggingService import log_error
from service.QueueMediaService import QueueMediaService
from service.videohosting_service.exception.DescriptionIsTooLongException import DescriptionIsTooLongException
from service.videohosting_service.exception.FileFormatException import FileFormatException
from service.videohosting_service.exception.FileSizeException import FileSizeException
from service.videohosting_service.exception.NameIsTooLongException import NameIsTooLongException
from service.videohosting_service.exception.VideoDurationException import VideoDurationException


class AddUploadQueueByDirectoryForm(QDialog):

    upload_targets = list()
    destination = None
    directory = None
    video_info = None
    passed = False

    def __init__(self, parent):

        super().__init__(parent)
        self.setWindowTitle(get_str('adding_video_via_url'))
        self.setFixedSize(500, 120)

        layout = QGridLayout()

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose)
        layout.addWidget(button_choose, 0, 0)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()
        self.event_service = EventService()
        self.queue_media_service = QueueMediaService()

    def choose(self):
        self.upload_targets = list()
        choose_accounts_for_uploading_form = ChooseAccountsForUploadingForm(self)
        choose_accounts_for_uploading_form.exec_()

        if choose_accounts_for_uploading_form.passed is False or len(choose_accounts_for_uploading_form.accounts) == 0:
            return

        accounts = choose_accounts_for_uploading_form.accounts
        for account in accounts:
            self.upload_targets.append({
                'login': account.login,
                'hosting': account.hosting,
                'upload_target': account.url})

        # form = DirOrFileForm(parent=self.parentWidget())
        # form.exec_()
        #
        # if form.passed is False:
        #     return
        #
        # file_need = form.file_need

        form = ChooseDirForm(parent=self.parentWidget(), file_need=True)
        form.exec_()

        if form.passed is False:
            return

        self.directory = form.choose_dir_button.text()
        self.video_info = list()

        for target in form.result:
            if os.path.isfile(target):
                handle_result = self.handle_file(target)
                if handle_result is not False:
                    self.video_info.append(handle_result)

        upload_interval = 0
        upload_interval_type = 0

        upload_hours = 0
        upload_minutes = 0

        if len(self.video_info) > 1:
            form = ChooseIntervalForm(self)
            form.exec_()

            if form.passed is False:
                return
            elif form.yes:
                upload_interval_type = form.upload_interval_type
                upload_interval = form.upload_interval
                upload_hours = form.upload_hours
                upload_minutes = form.upload_minutes

        elif len(self.video_info) == 0:
            return

        if upload_interval_type == 0:
            self.upload_in = relativedelta(minutes=upload_interval)
        elif upload_interval_type == 1:
            self.upload_in = relativedelta(hours=upload_interval)
        elif upload_interval_type == 2:
            self.upload_in = relativedelta(days=upload_interval)
        else:
            self.upload_in = relativedelta(months=upload_interval)

        self.first_upload_date = datetime.now()
        if self.first_upload_date.hour > upload_hours:
            self.first_upload_date = self.first_upload_date + timedelta(days=1)

        self.first_upload_date = self.first_upload_date.replace(minute=upload_minutes, hour=upload_hours)

        self.passed = True
        self.close()

    def handle_file(self, file_dir):
        upload_targets = list()
        upload = False

        for target in self.upload_targets:

            target_copy = target.copy()

            title = None
            description = None
            upload = False

            try:
                f = open(os.path.splitext(file_dir)[0] + '.info.json', 'r', encoding='utf-8')
                data = json.load(f)

                title = data['title']

                if 'description' in data:
                    description = data['description']
                f.close()
            except:
                log_error(f'{os.path.splitext(file_dir)[0]} - .info.json не найден')

            try:
                target_copy['title'] = title
                target_copy['description'] = description
                Hosting[target_copy['hosting']].value[0].validate_video_info_for_uploading(video_dir=file_dir)
            except VideoDurationException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_duration")}{file_dir}'))
                self.add_error_upload_item(file_dir, target_copy, f'{get_str("bad_file_duration")}{file_dir}')
                continue
            except FileSizeException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_size")}{file_dir}'))
                self.add_error_upload_item(file_dir, target_copy, f'{get_str("bad_file_size")}{file_dir}')
                continue
            except FileFormatException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_format")}{file_dir}'))
                self.add_error_upload_item(file_dir, target_copy, f'{get_str("bad_file_format")}{file_dir}')
                continue
            except Exception:
                continue

            if target_copy['title'] is None:
                form = TypeStrForm(parent=self, label=f'{get_str("input_title")}: {file_dir}')
                form.exec_()

                target_copy['title'] = form.str

            try:
                Hosting[target_copy['hosting']].value[0].validate_video_info_for_uploading(title=target_copy['title'])
            except NameIsTooLongException:
                while (Hosting[target_copy['hosting']].value[0].title_size_restriction is not None and \
                        len(target_copy['title']) > Hosting[target_copy['hosting']].value[0].title_size_restriction) or \
                        (Hosting[target_copy['hosting']].value[0].min_title_size is not None and \
                        len(target_copy['title']) < Hosting[target_copy['hosting']].value[0].min_title_size):
                    log_error(traceback.format_exc())
                    if Hosting[target_copy['hosting']].value[0].title_size_restriction is not None:
                        label = f'{get_str("bad_title")} ({str(Hosting[target_copy["hosting"]].value[0].min_title_size)} <= {get_str("name")} > {str(Hosting[target_copy["hosting"]].value[0].title_size_restriction)})'
                    else:
                        label = f'{get_str("bad_title")} ({str(Hosting[target_copy["hosting"]].value[0].min_title_size)} <= {get_str("name")})'
                    form = TypeStrForm(parent=self,
                                       label=label,
                                       current_text=target_copy['title'])
                    form.exec_()
                    target_copy['title'] = form.str

            if Hosting[target_copy['hosting']].value[0].description_size_restriction is not None:
                if target_copy['description'] is None:
                    form = TypeStrForm(parent=self, label=f'{get_str("input_description")}: {file_dir}')
                    form.exec_()

                    target_copy['description'] = form.str

                try:
                    Hosting[target_copy['hosting']].value[0].validate_video_info_for_uploading(description=target_copy['description'])
                except DescriptionIsTooLongException:
                    while len(target_copy['description']) > Hosting[target_copy['hosting']].value[0].description_size_restriction:
                        log_error(traceback.format_exc())
                        form = TypeStrForm(parent=self,
                                           label=f'{get_str("too_long_description")}{str(Hosting[target_copy["hosting"]].value[0].description_size_restriction)}',
                                           current_text=target_copy['description'])
                        form.exec_()
                        target_copy['description'] = form.str

            upload_targets.append(target_copy)
            upload = True
        if upload:
            return list([file_dir, title, description, datetime.now(), upload_targets])
        else:
            return False

    def add_error_upload_item(self, video_dir, target, error: str):
        self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(uuid.uuid4()),
                                                                          video_dir=video_dir,
                                                                          hosting=target['hosting'],
                                                                          status=3,
                                                                          account=self.state_service.get_account_by_hosting_and_login(
                                                                              target['hosting'],
                                                                              target['login'],
                                                                              target['upload_target']),
                                                                          destination=target[
                                                                              'upload_target'],
                                                                          upload_date=None,
                                                                          remove_files_after_upload=False,
                                                                          error_name=error))
