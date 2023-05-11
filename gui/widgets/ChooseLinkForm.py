from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QLineEdit, QMessageBox)

from model.Hosting import Hosting
from service.LocalizationService import *


# Этот QDialog предназначен для выбора аккаунта из числа доступных (см accounts в конструкторе)
class ChooseLinkForm(QDialog):
    account = None
    passed = False

    def __init__(self, parent: QWidget, hosting):
        super().__init__(parent)
        self.setWindowTitle(get_str('choose_link'))
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(f'<font size="4"> {get_str("choose_link")} </font>')
        self.link_edit = QLineEdit()

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.link_edit, 0, 1)

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose_link)
        layout.addWidget(button_choose, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.service = Hosting[hosting].value[0]

    def choose_link(self):
        if self.service.validate_page(self.link_edit.text()) == 2:
            self.passed = True
            self.close()
        else:
            msg = QMessageBox()
            msg.setText(get_str('bad_link'))
            msg.exec_()
