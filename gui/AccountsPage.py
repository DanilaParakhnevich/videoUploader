from PyQt5 import QtCore, QtWidgets

from gui.widgets.TypeUrlForm import TypeUrlForm
from model.Event import Event
from model.Hosting import Hosting
from gui.widgets.LoadingButton import AnimatedButton
from service.EventService import EventService
from service.LocalizationService import *


class AccountsPageWidget(QtWidgets.QTableWidget):
    comboBox = QtWidgets.QComboBox()

    state_service = StateService()
    event_service = EventService()

    accounts = state_service.get_accounts()

    def __init__(self, central_widget):
        super(AccountsPageWidget, self).__init__(central_widget)
        self.setMinimumSize(QtCore.QSize(0, 440))
        self.setObjectName("accounts_page_widget")
        self.setColumnCount(3)
        self.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(2, item)
        self.horizontalHeader().setDefaultSectionSize(310)

        horizontal_layout = QtWidgets.QHBoxLayout(self)
        horizontal_layout.setObjectName("horizontal_layout")

        self.comboBox.setParent(central_widget)
        for hosting in Hosting:
            self.comboBox.addItem(hosting.name)
        self.comboBox.setMaximumWidth(90)
        self.comboBox.setObjectName("comboBox")

        horizontal_layout.addWidget(self.comboBox)
        self.add_button = AnimatedButton(central_widget)
        self.add_button.setObjectName("add_button")
        horizontal_layout.addWidget(self.add_button)
        horizontal_layout.setAlignment(QtCore.Qt.AlignBottom)

        self.add_button.clicked.connect(self.on_add)

        item = self.horizontalHeaderItem(0)
        item.setText(get_str('videohosting'))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str('channel'))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str('delete'))
        self.add_button.setText(get_str('add'))

        for account in self.accounts:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(account.hosting)
            item2 = QtWidgets.QTableWidgetItem(account.url if hasattr(account, 'url') and account.url is not None else account.login)

            input_position = self.rowCount() - 1

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')
            self.setCellWidget(input_position, 2, btn)

            btn.clicked.connect(self.on_delete_row)

            self.setItem(input_position, 0, item1)
            self.setItem(input_position, 1, item2)

    def on_add(self):
        self.add_button.start_animation()
        hosting = Hosting[self.comboBox.currentText()]

        if hosting.value[0].need_to_pass_channel_after_login():
            form = TypeUrlForm(self, hosting)
            form.exec_()

            if form.passed is False:
                self.add_button.stop_animation()
                return

        account = hosting.value[0].show_login_dialog(hosting, self.parentWidget())
        msg = QtWidgets.QMessageBox(self)
        msg.setText(get_str('authorized_successfully'))

        if hosting.value[0].need_to_pass_channel_after_login():
            while hosting.value[0].validate_url_by_account(form.url, account) is False:
                form = TypeUrlForm(self, hosting, title=get_str("retype_url_for"))
                form.exec_()

                if form.passed is False:
                    self.add_button.stop_animation()
                    return

            account.url = form.url

        msg.exec_()

        if account is not None:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(self.comboBox.currentText())
            item2 = QtWidgets.QTableWidgetItem(account.url if account.url is not None else account.login)

            input_position = self.rowCount() - 1

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')
            self.setCellWidget(input_position, 2, btn)

            btn.clicked.connect(self.on_delete_row)

            self.setItem(input_position, 0, item1)
            self.setItem(input_position, 1, item2)
            self.event_service.add_event(Event(
                f'{get_str("event_loginned")} {account.login}, {self.comboBox.currentText()}'))

        self.add_button.stop_animation()

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            self.removeRow(row)
            self.accounts.pop(row)
            self.state_service.save_accounts(self.accounts)
