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

    def ok(self):
        if self.choose_dir_button.text() != '':
            self.passed = True
            self.close()
        else:
            msg = QMessageBox()
            msg.setText(get_str('bad_dir'))
            msg.exec_()

    def pick_new(self):
        sorter = QtCore.QSortFilterProxyModel()
        sorter.setDynamicSortFilter(True)

        if self.file_need:
            folder_path = QFileDialog.getOpenFileName(self, get_str('choose_file'))
        else:
            folder_path = QFileDialog.getExistingDirectory(self, get_str('choose_dir'))

        if folder_path != '':
            if type(folder_path) is tuple:
                folder_path = folder_path[0]
            self.choose_dir_button.setText(folder_path)