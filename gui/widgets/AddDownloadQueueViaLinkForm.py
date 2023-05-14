import traceback

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout, QCheckBox)
from PyQt5.QtCore import QRect

from gui.widgets.ChooseVideoQualityComboBox import ChooseVideoQualityComboBox
from gui.widgets.FormatChooserComboBox import FormatChooserComboBox
from gui.widgets.TypeStrForm import TypeStrForm
from gui.widgets.UploadAfterDownloadForm import UploadAfterDownloadForm
from model.Hosting import Hosting
from service.LocalizationService import *
from gui.widgets.ChooseAccountForm import ChooseAccountForm
from gui.widgets.ChooseLinkForm import ChooseLinkForm
from service.LoggingService import log_error
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
    upload_account = None
    upload_target = None
    upload_hosting = None
    title = None
    description = None

    def __init__(self, parent):

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
        
        self.choose_video_format_combo_box = FormatChooserComboBox(self)
        self.choose_video_format_combo_box.setGeometry(QRect(620, 100, 300, 30))
        self.choose_video_format_combo_box.setObjectName('choose_video_format_combo_box')
        self.choose_video_format_combo_box.setCurrentIndex(0)

        layout.addWidget(self.choose_video_format_combo_box, 1, 1)

        self.choose_video_quality_combo_box = ChooseVideoQualityComboBox(self)
        self.choose_video_quality_combo_box.setGeometry(QRect(620, 150, 300, 30))
        self.choose_video_quality_combo_box.setObjectName('choose_video_quality_form')
        self.choose_video_quality_combo_box.setCurrentIndex(0)

        layout.addWidget(self.choose_video_quality_combo_box, 2, 1)

        remove_files_after_upload_label = QLabel()
        remove_files_after_upload_label.setText(get_str('remove_files_after_upload'))
        remove_files_after_upload_label.setGeometry(QRect(670, 200, 250, 30))
        remove_files_after_upload_label.setObjectName('remove_files_after_upload_label')

        layout.addWidget(remove_files_after_upload_label, 3, 0)

        self.remove_files_after_upload = QCheckBox()
        self.remove_files_after_upload.setGeometry(QRect(620, 200, 30, 30))
        self.remove_files_after_upload.setObjectName('remove_files_after_upload')
        self.remove_files_after_upload.setChecked(False)

        layout.addWidget(self.remove_files_after_upload, 3, 1)

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose)
        layout.addWidget(button_choose, 4, 0, 1, 2)
        layout.setRowMinimumHeight(4, 75)

        self.setLayout(layout)
        self.state_service = StateService()

    def choose(self):
        accounts = self.state_service.get_accounts_by_hosting(self.hosting_combo_box.currentText())

        if len(accounts) == 0 and Hosting[self.hosting_combo_box.currentText()].value[1]:
            msg = QMessageBox()
            msg.setText(get_str('need_authorize'))
            msg.exec_()
            return
        else:
            form = ChooseAccountForm(parent=self.parentWidget(),
                                     accounts=accounts)
            form.exec_()

            if form.account is None and Hosting[self.hosting_combo_box.currentText()].value[1]:
                return

        self.account = form.account
        self.hosting = self.hosting_combo_box.itemData(self.hosting_combo_box.currentIndex())

        form = ChooseLinkForm(parent=self.parentWidget(), hosting=self.hosting_combo_box.currentText())
        form.exec_()

        if form.passed is False:
            return

        self.link = form.link_edit.text()
        if self.choose_video_format_combo_box.currentIndex() != 3:
            form = UploadAfterDownloadForm(self, need_interval=False)
            form.exec_()

            if form.passed is False:
                self.close()
                return

            self.upload_on = form.upload_flag
            self.upload_hosting = form.upload_hosting

            if self.upload_on:
                video_info = self.hosting.value[0].get_video_info(self.link,
                                                             self.choose_video_quality_combo_box.itemData(self.choose_video_quality_combo_box.currentIndex()),
                                                             self.account)
                try:
                    self.upload_hosting.value[0].validate_video_info_for_uploading(title=video_info['title'],
                                                                              description=video_info[
                                                                                  'description'],
                                                                              duration=video_info[
                                                                                  'duration'],
                                                                              filesize=video_info[
                                                                                  'filesize'],
                                                                              ext=video_info['ext'])
                except VideoDurationException:
                    log_error(traceback.format_exc())
                    msg = QMessageBox()
                    msg.setText(f'{get_str("bad_file_duration")}{video_info["title"]}')
                    msg.exec_()
                    self.upload_on = False
                except FileSizeException:
                    log_error(traceback.format_exc())
                    msg = QMessageBox()
                    msg.setText(f'{get_str("bad_file_size")}{video_info["title"]}')
                    msg.exec_()
                    self.upload_on = False
                except FileFormatException:
                    log_error(traceback.format_exc())
                    msg = QMessageBox()
                    msg.setText(f'{get_str("bad_file_format")}{video_info["title"]}')
                    msg.exec_()
                    self.upload_on = False
                except NameIsTooLongException:
                    self.title = video_info['title']
                    while len(self.title) > self.upload_hosting.value[0].title_size_restriction:
                        log_error(traceback.format_exc())
                        form = TypeStrForm(parent=self,
                                           label=f'{get_str("too_long_title")}{str(self.upload_hosting.value[0].title_size_restriction)}',
                                           current_text=self.title)
                        form.exec_()
                        self.title = form.str

                except DescriptionIsTooLongException:
                    self.description = video_info['description']
                    while len(self.description) > self.upload_hosting.value[0].description_size_restriction:
                        log_error(traceback.format_exc())
                        form = TypeStrForm(parent=self,
                                           label=f'{get_str("too_long_description")}{str(self.upload_hosting.value[0].description_size_restriction)}',
                                           current_text=self.description)
                        form.exec_()
                        self.description = form.str

            self.upload_account = form.upload_account
            self.upload_target = form.upload_target

        self.video_quality = self.choose_video_quality_combo_box.itemData(self.choose_video_quality_combo_box.currentIndex())
        self.format = self.choose_video_format_combo_box.itemData(self.choose_video_format_combo_box.currentIndex())
        self.passed = True
        self.close()
