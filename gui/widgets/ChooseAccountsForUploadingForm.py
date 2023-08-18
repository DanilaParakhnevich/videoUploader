from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from gui.widgets.AccountsListWidget import AccountsListWidget
from service.LocalizationService import *


class ChooseAccountsForUploadingForm(QDialog):
    accounts = list()
    passed = False

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.state_service = StateService()
        self.setWindowTitle(get_str('choose_channels_for_uploading'))
        self.resize(state_service.get_accounts_list_widget_size()[0], state_service.get_accounts_list_widget_size()[1])

        layout = QGridLayout()

        self.accounts_list_widget = AccountsListWidget(self, self.state_service.get_accounts())

        layout.addWidget(self.accounts_list_widget, 0, 0)

        button_login = QPushButton(get_str('choose'))
        button_login.clicked.connect(self.choose_accounts)
        layout.addWidget(button_login, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.accounts = list()
        self.setLayout(layout)

    def resizeEvent(self, event):
        self.not_resize = True
        state_service.save_accounts_list_widget_size(self.width(), self.height())
        coef_x = self.width() / 500

        self.accounts_list_widget.setColumnWidth(0, int(self.state_service.get_tab_column_weight(
            'acc_list_widget', 0, start_width=460, count=3) * coef_x))

        self.accounts_list_widget.setColumnWidth(1, int(self.state_service.get_tab_column_weight(
            'acc_list_widget', 1, start_width=460, count=3) * coef_x))

        self.accounts_list_widget.setColumnWidth(2, int(self.state_service.get_tab_column_weight(
            'acc_list_widget', 2, start_width=460, count=3) * coef_x))
        super().resizeEvent(event)
        self.not_resize = False


    def choose_accounts(self):
        for i in range(0, self.accounts_list_widget.rowCount()):
            if self.accounts_list_widget.item(i, 2).checkState() != 0:
                hosting = self.accounts_list_widget.item(i, 1).text()
                login = self.accounts_list_widget.item(i, 0).text()
                by_login = self.state_service.get_account_by_hosting_and_login(hosting, login)
                by_url = self.state_service.get_account_by_hosting_and_url(hosting, login)
                self.accounts.append(by_url if by_url is not None else by_login)
        self.passed = True
        self.close()
