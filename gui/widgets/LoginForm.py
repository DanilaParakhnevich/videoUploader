from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)

from model.Account import Account
from service.videohosting_service.VideohostingService import VideohostingService
from service.LocalizationService import *
from service.StateService import StateService
from logging import *
import traceback


class LoginForm(QDialog):
    account = None
    passed = False

    def __init__(self, parent: QWidget, hosting, service: VideohostingService, count: int,
                 username: str = get_str('username'), password:str = get_str('password'), username_val=''):
        super().__init__(parent)
        self.setWindowTitle('Login Form')
        self.resize(500, 120)

        layout = QGridLayout()

        # В некоторых ситуациях, невозможно при помощи вебдрайвера засетать юсернейм и пароль, поэтому иногда даем
        # возможность обойтись без пароля и просто дать название аккаунту для дальнейшего использования
        if count == 2:
            label_name = QLabel(f'<font size="4"> {username} </font>')
            self.lineEdit_username = QLineEdit()
            layout.addWidget(label_name, 0, 0)
            layout.addWidget(self.lineEdit_username, 0, 1)

            label_password = QLabel(f'<font size="4"> {password} </font>')
            self.lineEdit_password = QLineEdit()
            layout.addWidget(label_password, 1, 0)
            layout.addWidget(self.lineEdit_password, 1, 1)
        else:
            label_name = QLabel(f'<font size="4"> {username} </font>')
            self.lineEdit_username = QLineEdit()
            layout.addWidget(label_name, 0, 0)
            layout.addWidget(self.lineEdit_username, 0, 1)

            self.lineEdit_password = QLineEdit()

        button_login = QPushButton(get_str('login'))
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)
        self.lineEdit_username.setText(username_val)

        self.setLayout(layout)
        self.hosting = hosting
        self.service = service
        self.state_service = StateService()

    def check_password(self):
        msg = QMessageBox()

        if self.hosting.value[0].need_to_pass_channel_after_login() is False:
            for account in self.state_service.get_accounts_by_hosting(self.hosting.name):
                if account.login == self.lineEdit_username.text():
                    msg.setText(get_str('account_already_exists'))
                    msg.exec_()
                    return

        try:
            auth = self.service.login(self.lineEdit_username.text(), self.lineEdit_password.text())
        except:
            error(traceback.format_exc())
            msg.setText(get_str("entered_incorrect_data"))
            msg.exec_()
            self.close()
            return

        self.account = Account(hosting=self.hosting.name,
                               login=self.lineEdit_username.text(),
                               password=self.lineEdit_password.text(),
                               auth=auth)
        self.passed = True
        self.close()
