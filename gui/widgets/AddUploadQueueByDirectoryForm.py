import traceback
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout)
from dateutil.relativedelta import relativedelta

from gui.widgets.ChooseAccountsForUploadingForm import ChooseAccountsForUploadingForm
from model.Event import Event
from model.Hosting import Hosting
from service.EventService import EventService
from service.LocalizationService import *
from gui.widgets.ChooseDirForm import ChooseDirForm
from gui.widgets.DirOrFileForm import DirOrFileForm
from gui.widgets.TypeStrForm import TypeStrForm
from gui.widgets.ChooseIntervalsForm import ChooseIntervalForm
import os

from service.LoggingService import log_error
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
        self.resize(500, 120)

        layout = QGridLayout()

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose)
        layout.addWidget(button_choose, 0, 0)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()
        self.event_service = EventService()

    def choose(self):
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

        form = DirOrFileForm(parent=self.parentWidget())
        form.exec_()

        if form.passed is False:
            return

        file_need = form.file_need

        form = ChooseDirForm(parent=self.parentWidget(), file_need=file_need)
        form.exec_()

        if form.passed is False:
            return

        self.directory = form.choose_dir_button.text()

        self.video_info = list()

        if os.path.isdir(self.directory):
            for target in os.listdir(self.directory):
                if os.path.isfile(f'{self.directory}/{target}'):
                    handle_result = self.handle_file(f'{self.directory}/{target}')
                    if handle_result is not False:
                        self.video_info.append(handle_result)

            upload_interval = 0
            upload_interval_type = 0

            if len(self.video_info) > 1:
                form = ChooseIntervalForm(self)
                form.exec_()

                if form.passed is False:
                    return
                elif form.yes:
                    upload_interval_type = form.upload_interval_type
                    upload_interval = form.upload_interval
            elif len(self.video_info) == 0:
                return

            upload_date = datetime.now()

            for info in self.video_info:
                info[3] = upload_date

                if upload_interval_type == 0:
                    upload_date = upload_date + relativedelta(minutes=upload_interval)
                elif upload_interval_type == 1:
                    upload_date = upload_date + relativedelta(hours=upload_interval)
                elif upload_interval_type == 2:
                    upload_date = upload_date + relativedelta(days=upload_interval)
                else:
                    upload_date = upload_date + relativedelta(months=upload_interval)

        else:
            handle_result = self.handle_file(self.directory)
            if handle_result is not False:
                handle_result.append(datetime.now())
                self.video_info.append(handle_result)

        self.passed = True
        self.close()

    def handle_file(self, file_dir):
        title = None
        description = None
        upload = False
        upload_targets = list()

        for target in self.upload_targets:
            try:
                Hosting[target['hosting']].value[0].validate_video_info_for_uploading(video_dir=file_dir)
            except VideoDurationException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_duration")}{file_dir}'))
                continue
            except FileSizeException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_size")}{file_dir}'))
                continue
            except FileFormatException:
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("bad_file_format")}{file_dir}'))
                continue

            if Hosting[target['hosting']].value[0].title_size_restriction is not None and title is None:
                form = TypeStrForm(parent=self, label=f'{get_str("input_title")}: {file_dir}')
                form.exec_()

                title = form.str

                if form.passed:
                    try:
                        Hosting[target['hosting']].value[0].validate_video_info_for_uploading(title=title)
                    except NameIsTooLongException:
                        while len(title) > Hosting[target['hosting']].value[0].title_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=self,
                                               label=f'{get_str("too_long_title")}{str(Hosting[target["hosting"]].value[0].title_size_restriction)}',
                                               current_text=title)
                            form.exec_()
                            title = form.str

                else:
                    continue

            if Hosting[target['hosting']].value[0].description_size_restriction is not None and description is None:
                form = TypeStrForm(parent=self, label=f'{get_str("input_description")}: {file_dir}')
                form.exec_()

                description = form.str

                if form.passed:
                    try:
                        Hosting[target['hosting']].value[0].validate_video_info_for_uploading(description=description)
                    except DescriptionIsTooLongException:
                        while len(description) > Hosting[target['hosting']].value[0].description_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=self,
                                               label=f'{get_str("too_long_description")}{str(Hosting[target["hosting"]].value[0].description_size_restriction)}',
                                               current_text=description)
                            form.exec_()
                            description = form.str
                else:
                    continue

            upload_targets.append(target)
            upload = True
        if upload:
            return list([file_dir, title, description, datetime.now(), upload_targets])
        else:
            return False
