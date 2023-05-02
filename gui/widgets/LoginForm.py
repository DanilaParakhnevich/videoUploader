from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)

from model.Account import Account
from service.videohosting_service.VideohostingService import VideohostingService
from service.StateService import StateService


class LoginForm(QDialog):
    account = None

    def __init__(self, parent: QWidget, hosting, service: VideohostingService, count: int, usernamePlaceholder: str = 'Please enter your username', passwordPlaceholder: str = 'Please enter your password'):
        super().__init__(parent)
        self.setWindowTitle('Login Form')
        self.resize(500, 120)

        layout = QGridLayout()

        if count == 2:
            label_name = QLabel('<font size="4"> Username </font>')
            self.lineEdit_username = QLineEdit()
            self.lineEdit_username.setPlaceholderText(usernamePlaceholder)
            layout.addWidget(label_name, 0, 0)
            layout.addWidget(self.lineEdit_username, 0, 1)

            label_password = QLabel('<font size="4"> Password </font>')
            self.lineEdit_password = QLineEdit()
            self.lineEdit_password.setPlaceholderText(passwordPlaceholder)
            layout.addWidget(label_password, 1, 0)
            layout.addWidget(self.lineEdit_password, 1, 1)
        else:
            label_name = QLabel('<font size="4"> Username </font>')
            self.lineEdit_username = QLineEdit()
            self.lineEdit_username.setPlaceholderText(usernamePlaceholder)
            layout.addWidget(label_name, 0, 0)
            layout.addWidget(self.lineEdit_username, 0, 1)

            self.lineEdit_password = QLineEdit()


        self.label_error = QLabel('<font size="4">Введены неверные данные</font>')
        self.label_error.hide()
        layout.addWidget(self.label_error, 2, 0)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.hosting = hosting
        self.service = service
        self.state_service = StateService()

    def check_password(self):
        msg = QMessageBox()

        for account in self.state_service.get_accounts_by_hosting(self.hosting.name):
            if account.login == self.lineEdit_username.text():
                msg.setText('Такой аккаунт уже существует')
                msg.exec_()
                return

        try:
            token = self.service.login(self.lineEdit_username.text(), self.lineEdit_password.text())
        except:
            self.label_error.show()
            return

        msg.setText('Вы успешно авторизованы')

        current_accounts = self.state_service.get_accounts()
        self.account = Account(hosting=self.hosting.name,
                               login=self.lineEdit_username.text(),
                               password=self.lineEdit_password.text(),
                               auth=token)

        current_accounts.append(self.account)

        self.state_service.save_accounts(current_accounts)

        msg.exec_()
        self.label_error.hide()
        self.close()
