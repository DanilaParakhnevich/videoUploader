import traceback
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout)
from dateutil.relativedelta import relativedelta

from gui.widgets.ChooseAccountsForUploadingForm import ChooseAccountsForUploadingForm
from gui.widgets.ChooseChannelForm import ChooseChannelForm
from model.Hosting import Hosting
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

    def choose(self):
        choose_accounts_for_uploading_form = ChooseAccountsForUploadingForm(self)
        choose_accounts_for_uploading_form.exec_()

        if choose_accounts_for_uploading_form.passed is False or len(choose_accounts_for_uploading_form.accounts) == 0:
            return

        self.accounts = choose_accounts_for_uploading_form.accounts

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

        for account in self.accounts:
            try:
                Hosting[account.hosting].value[0].validate_video_info_for_uploading(video_dir=file_dir)
            except Exception as error:
                msg = QMessageBox()
                msg.setText(error.__str__())
                msg.exec_()
                continue

            if Hosting[account.hosting].value[0].title_size_restriction is not None and title is None:
                form = TypeStrForm(parent=self, label=f'{get_str("input_title")}: {file_dir}')
                form.exec_()

                title = form.str

                if form.passed:
                    try:
                        Hosting[account.hosting].value[0].validate_video_info_for_uploading(video_dir=file_dir, title=title)
                    except VideoDurationException:
                        log_error(traceback.format_exc())
                        msg = QMessageBox()
                        msg.setText(f'{get_str("bad_file_duration")}{file_dir}')
                        msg.exec_()
                    except FileSizeException:
                        log_error(traceback.format_exc())
                        msg = QMessageBox()
                        msg.setText(f'{get_str("bad_file_size")}{file_dir}')
                        msg.exec_()
                    except FileFormatException:
                        log_error(traceback.format_exc())
                        msg = QMessageBox()
                        msg.setText(f'{get_str("bad_file_format")}{file_dir}')
                        msg.exec_()
                    except NameIsTooLongException:
                        while len(title) > Hosting[account.hosting].value[0].title_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=self,
                                               label=f'{get_str("too_long_title")}{str(Hosting[account.hosting].value[0].title_size_restriction)}',
                                               current_text=title)
                            form.exec_()
                            title = form.str

                else:
                    continue

            if Hosting[account.hosting].value[0].description_size_restriction is not None and description is None:
                form = TypeStrForm(parent=self, label=f'{get_str("input_description")}: {file_dir}')
                form.exec_()

                description = form.str

                if form.passed:
                    try:
                        Hosting[account.hosting].value[0].validate_video_info_for_uploading(description=description)
                    except DescriptionIsTooLongException:
                        while len(description) > Hosting[account.hosting].value[0].description_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=self,
                                               label=f'{get_str("too_long_description")}{str(Hosting[account.hosting].value[0].description_size_restriction)}',
                                               current_text=description)
                            form.exec_()
                            description = form.str
                else:
                    continue

            if Hosting[account.hosting].value[0].need_to_be_uploaded_to_special_source():
                # В некоторых ситуациях, допустим с Telegram, для выгрузки необходимо указать дополнительную информацию
                # такую, как то, на какой именно канал по аккаунту нужно выгружать видео

                channels = self.state_service.get_channel_by_hosting(account.hosting)

                if len(channels) == 0:
                    msg = QMessageBox()
                    msg.setText(
                        f'{get_str("not_found_channels_for_videohosting")}: {account.hosting}')
                    msg.exec_()
                    self.close()
                    continue

                form = ChooseChannelForm(self, channels)
                form.exec_()

                if form.passed:
                    self.upload_targets.append({
                        'login': account.login,
                        'hosting': account.hosting,
                        'upload_target': form.channel.url
                    })
                else:
                    self.close()
                    continue
            else:
                self.upload_targets.append({
                    'login': account.login,
                    'hosting': account.hosting,
                    'upload_target': None
                })

        return list([file_dir, title, description, datetime.now()])
