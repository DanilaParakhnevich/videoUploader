from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QFileDialog, QMessageBox)

from service.LocalizationService import *


class ConfirmExitForm(QDialog):

    confirmed = False
    passed = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_str('confirm_exit'))
        self.resize(500, 120)

        self.gridLayout = QGridLayout(self)

        self.yes_button = QPushButton()
        self.yes_button.setMaximumWidth(200)
        self.yes_button.setText(get_str('yes'))
        self.yes_button.clicked.connect(self.yes)

        self.no_button = QPushButton()
        self.no_button.setMaximumWidth(200)
        self.no_button.setText(get_str('no'))
        self.no_button.clicked.connect(self.no)

        self.gridLayout.addWidget(self.yes_button, 0, 1)
        self.gridLayout.addWidget(self.no_button, 0, 2)

    def yes(self):
        self.confirmed = True
        self.passed = True
        self.close()

    def no(self):
        self.passed = True
        self.close()
