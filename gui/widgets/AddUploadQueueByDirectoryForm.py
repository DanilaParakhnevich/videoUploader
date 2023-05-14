from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout)
from dateutil.relativedelta import relativedelta

from gui.widgets.ChooseChannelForm import ChooseChannelForm
from model.Hosting import Hosting
from service.LocalizationService import *
from gui.widgets.ChooseAccountForm import ChooseAccountForm
from gui.widgets.ChooseDirForm import ChooseDirForm
from gui.widgets.DirOrFileForm import DirOrFileForm
from gui.widgets.TypeStrForm import TypeStrForm
from gui.widgets.ChooseIntervalsForm import ChooseIntervalForm
import os

class AddUploadQueueByDirectoryForm(QDialog):

    account = None
    hosting = None
    destination = None
    directory = None
    video_info = None
    passed = False

    def __init__(self, parent):

        super().__init__(parent)
        self.setWindowTitle(get_str('adding_video_via_url'))
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(f'<font size="4"> {get_str("videohosting")} </font>')
        self.combo_box = QComboBox()

        for hosting in Hosting:
            self.combo_box.addItem(hosting.name, hosting)

        self.combo_box.setCurrentIndex(0)

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.combo_box, 0, 1)

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose)
        layout.addWidget(button_choose, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()

    def choose(self):

        self.hosting = self.combo_box.currentData()

        accounts = self.state_service.get_accounts_by_hosting(self.hosting.name)

        if len(accounts) == 0:
            msg = QMessageBox()
            msg.setText(get_str('need_authorize'))
            msg.exec_()
            return
        else:
            form = ChooseAccountForm(parent=self.parentWidget(),
                                     accounts=accounts)
            form.exec_()

            if form.account is None:
                return

        self.account = form.account

        if self.hosting.value[0].need_to_be_uploaded_to_special_source():
            channels = self.state_service.get_channel_by_hosting(self.hosting.name)

            if len(channels) == 0:
                msg = QMessageBox()
                msg.setText(get_str('need_create_some_channel'))
                msg.exec_()
                return

            form = ChooseChannelForm(self, channels)
            form.exec_()

            if form.passed:
                self.destination = form.channel.url
            else:
                return

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

            form = ChooseIntervalForm(self)
            form.exec_()

            if form.passed is False:
                return

            upload_interval = 0
            upload_interval_type = 0

            if form.passed is False:
                return
            elif form.yes:
                upload_interval_type = form.upload_interval_type
                upload_interval = form.upload_interval

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
        try:
            self.hosting.value[0].validate_video_info_for_uploading(video_dir=file_dir)
        except Exception as error:
            msg = QMessageBox()
            msg.setText(error.__str__())
            msg.exec_()
            return False

        title = None
        description = None

        if self.hosting.value[0].title_size_restriction is not None:
            while True:
                form = TypeStrForm(parent=self, label=get_str('input_title'))
                form.exec_()

                title = form.str

                if form.passed:
                    try:
                        self.hosting.value[0].validate_video_info_for_uploading(video_dir=file_dir, title=title)
                        break
                    except:
                        msg = QMessageBox()
                        msg.setText(get_str('too_long_title') + self.hosting.value[0].title_size_restriction)
                        msg.exec_()
                else:
                    return False

        if self.hosting.value[0].description_size_restriction is not None:
            while True:
                form = TypeStrForm(parent=self, label=get_str('input_description'))
                form.exec_()

                description = form.str

                if form.passed:
                    try:
                        self.hosting.value[0].validate_video_info_for_uploading(video_dir=file_dir, description=description)
                        break
                    except:
                        msg = QMessageBox()
                        msg.setText(get_str('too_long_description') + self.hosting.value[0].description_size_restriction)
                        msg.exec_()
                else:
                    return False

        return list([file_dir, title, description, datetime.now()])
