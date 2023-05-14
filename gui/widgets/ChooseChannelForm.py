from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from service.LocalizationService import *


# Этот QDialog предназначен для выбора аккаунта из числа доступных (см accounts в конструкторе)
class ChooseChannelForm(QDialog):
    account = None
    passed = False

    def __init__(self, parent: QWidget, channels):
        super().__init__(parent)
        self.setWindowTitle(get_str('choose_channel_for_uploading'))
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(get_str("choose_channel_for_uploading"))
        self.combo_box = QComboBox()

        for channel in channels:
            self.combo_box.addItem(channel.url, channel)

        self.combo_box.setCurrentIndex(0)

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.combo_box, 0, 1)

        button_login = QPushButton(get_str('choose'))
        button_login.clicked.connect(self.choose_account)
        layout.addWidget(button_login, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()

    def choose_account(self):
        self.channel = self.combo_box.currentData()
        self.passed = True
        self.close()
