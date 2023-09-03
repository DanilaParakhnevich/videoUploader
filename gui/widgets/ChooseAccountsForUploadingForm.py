from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox, QLineEdit)

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

        self.search = QLineEdit(self)
        self.accounts_list_widget = AccountsListWidget(self, self.state_service.get_accounts())

        layout.addWidget(self.search, 0, 0)
        layout.addWidget(self.accounts_list_widget, 1, 0)

        button_login = QPushButton(get_str('choose'))
        button_login.clicked.connect(self.choose_accounts)
        layout.addWidget(button_login, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.accounts = list()
        self.setLayout(layout)
        self.search.textChanged.connect(self.findName)
        self.search.setText(self.state_service.get_name('edit_name'))

    def findName(self):
        name = self.search.text().lower()
        self.state_service.save_name('edit_name', name)
        for row in range(self.accounts_list_widget.rowCount()):
            item = self.accounts_list_widget.item(row, 1)
            # if the search is *not* in the item's text *do not hide* the row
            self.accounts_list_widget.setRowHidden(row, name not in item.text().lower())

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
