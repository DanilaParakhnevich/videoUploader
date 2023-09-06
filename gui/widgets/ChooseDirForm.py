from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QFileDialog, QMessageBox)

from service.LocalizationService import *


class ChooseDirForm(QDialog):

    passed = False

    def __init__(self, parent: QWidget, file_need):
        super().__init__(parent)
        self.setWindowTitle(get_str('choose_the_dir'))
        self.setFixedSize(500, 120)

        self.gridLayout = QGridLayout(self)

        self.choose_dir_button = QPushButton()
        self.choose_dir_button.setObjectName("choose_dir_button")
        self.choose_dir_button.setMaximumWidth(200)
        self.choose_dir_button.clicked.connect(self.pick_new)
        self.gridLayout.addWidget(self.choose_dir_button, 2, 1)
        self.choose_dir_label = QLabel()
        self.choose_dir_label.setObjectName("choose_dir_label")
        self.choose_dir_label.setText(get_str('choose_the_dir'))
        self.gridLayout.addWidget(self.choose_dir_label, 2, 0)

        self.ok_button = QPushButton()
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setMaximumWidth(200)
        self.ok_button.setText(get_str('choose'))
        self.ok_button.clicked.connect(self.ok)

        self.file_need = file_need
        self.gridLayout.addWidget(self.ok_button, 3, 1)
        self.state_service = StateService()

    def ok(self):
        if self.choose_dir_button.text() != '':
            self.passed = True
            self.close()
        else:
            msg = QMessageBox()
            msg.setText(get_str('bad_dir'))
            msg.exec_()

    def pick_new(self):
        qfdlg = QFileDialog(None, get_str('choose_dir'))

        qfdlg.setOption(QFileDialog.DontUseNativeDialog, False)

        self.state_service.q_settings.beginGroup("fileopendlg")
        qfdlg.restoreState(self.state_service.q_settings.value("savestate_upload", qfdlg.saveState()))
        qfdlg.setDirectory(self.state_service.q_settings.value("savestate_upload_dir"))
        self.state_service.q_settings.endGroup()

        qfdlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        qfdlg.setWindowTitle(get_str('choose_file'))

        result = qfdlg.exec_()

        if result:
            self.choose_dir_button.setText(qfdlg.directory().path())

        self.result = qfdlg.selectedFiles()

        self.state_service.q_settings.beginGroup("fileopendlg")
        self.state_service.q_settings.setValue("savestate_upload", qfdlg.saveState())
        self.state_service.q_settings.setValue("savestate_upload_dir", qfdlg.directory().path())
        self.state_service.q_settings.endGroup()
        self.passed = True
        self.close()
