from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from service.StateService import StateService


class ChooseAccountForm(QDialog):
    account = None

    def __init__(self, parent: QWidget, accounts, choose_account_text='Выберите аккаунт'):
        super().__init__(parent)
        self.setWindowTitle(choose_account_text)
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(f'<font size="4"> {choose_account_text} </font>')
        self.combo_box = QComboBox()
        self.combo_box.setPlaceholderText(choose_account_text)

        for account in accounts:
            self.combo_box.addItem(account.login, account)

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.combo_box, 0, 1)

        button_login = QPushButton('Выбрать')
        button_login.clicked.connect(self.choose_account)
        layout.addWidget(button_login, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()

    def choose_account(self):
        self.account = self.combo_box.currentData()
        self.close()
