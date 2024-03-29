import traceback
from functools import partial

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer

from gui.widgets.ComboBoxWithCompleter import ComboBoxWithCompleter
from gui.widgets.TypeUrlForm import TypeUrlForm
from model.Event import Event
from model.Hosting import Hosting
from gui.widgets.LoadingButton import AnimatedButton
from service.EventService import EventService
from service.LocalizationService import *
from service.LoggingService import log_error
from service.QueueMediaService import QueueMediaService


class AccountsPageWidget(QtWidgets.QTableWidget):
    comboBox = ComboBoxWithCompleter()

    state_service = StateService()
    event_service = EventService()

    accounts = state_service.get_accounts()

    def __init__(self, central_widget):
        super(AccountsPageWidget, self).__init__(central_widget)
        self.setMinimumSize(QtCore.QSize(0, 440))
        self.setObjectName("accounts_page_widget")
        self.setColumnCount(4)
        self.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(3, item)
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
        item.setText(get_str('reauthorize'))
        item = self.horizontalHeaderItem(3)
        item.setText(get_str('delete'))
        self.add_button.setText(get_str('add'))

        for account in self.accounts:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(account.hosting)
            item2 = QtWidgets.QTableWidgetItem(account.url if hasattr(account, 'url') and account.url is not None else account.login)

            input_position = self.rowCount() - 1

            btn = QtWidgets.QPushButton(self)
            btn.setText(get_str('reauthorize'))
            btn.clicked.connect(partial(self.reauthorize, account.url if hasattr(account, 'url') and account.url is not None else account.login, account.hosting))
            self.setCellWidget(input_position, 2, btn)

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')
            btn.clicked.connect(self.on_delete_row)
            self.setCellWidget(input_position, 3, btn)

            self.setItem(input_position, 0, item1)
            self.setItem(input_position, 1, item2)

        self.horizontalHeader().sectionResized.connect(self.section_resized)

        self.queue_media_service = QueueMediaService()
        self.updating_accounts = QTimer(self)
        self.updating_accounts.timeout.connect(self.update_accounts)
        self.updating_accounts.start(3_000)

    def update_accounts(self):
        for dict in self.queue_media_service.get_reauthorized_accounts_from_upload_page():
            i = 0
            for account in self.accounts:
                if account.url == dict[1].url and account.login == dict[1].login and account.hosting == dict[1].hosting:

                    if dict[1].url is not None:
                        item = dict[1].url
                    else:
                        item = dict[1].login

                    self.item(i, 1).setText(item)

                i = i + 1

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

        if account is None:
            self.add_button.stop_animation()
            return

        msg = QtWidgets.QMessageBox(self)
        msg.setText(get_str('authorized_successfully'))

        if hosting.value[0].need_to_pass_channel_after_login():
            try:
                while hosting.value[0].validate_url_by_account(form.url, account) is False:
                    form = TypeUrlForm(self, hosting, title=get_str("retype_url_for"))
                    form.exec_()

                    if form.passed is False:
                        self.add_button.stop_animation()
                        return

                account.url = form.url
            except:
                msg = QtWidgets.QMessageBox(self)
                msg.setText(f'{get_str("failed_account_validation")}: {form.url}')
                msg.exec_()
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("failed_account_validation")}: {form.url}'))
                self.add_button.stop_animation()
                return

        msg.exec_()

        if account is not None:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(self.comboBox.currentText())
            item2 = QtWidgets.QTableWidgetItem(account.url if account.url is not None else account.login)

            input_position = self.rowCount() - 1

            btn = QtWidgets.QPushButton(self)
            btn.setText(get_str('reauthorize'))
            btn.clicked.connect(partial(self.reauthorize, account.url if hasattr(account, 'url') and account.url is not None else account.login))
            self.setCellWidget(input_position, 2, btn)

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')
            self.setCellWidget(input_position, 3, btn)

            btn.clicked.connect(self.on_delete_row)

            self.setItem(input_position, 0, item1)
            self.setItem(input_position, 1, item2)
            self.event_service.add_event(Event(
                f'{get_str("event_loginned")} {account.login}, {self.comboBox.currentText()}'))

            current_accounts = self.state_service.get_accounts()
            current_accounts.append(account)
            self.state_service.save_accounts(current_accounts)

        self.add_button.stop_animation()

    def reauthorize(self, name, hosting):
        by_login = self.state_service.get_account_by_hosting_and_login(hosting, name)
        by_url = self.state_service.get_account_by_hosting_and_url(hosting, name)
        account = by_url if by_url is not None else by_login
        hosting = Hosting[hosting]

        acc_temp = account

        account = hosting.value[0].show_login_dialog(hosting, form=self, title='check_fail',
                                                     login=account.login,
                                                     password=account.password if self.state_service.get_settings().save_password else '',
                                                     can_relogin=True)

        if account is None:
            return

        index = 0
        for acc in self.state_service.get_accounts():
            if acc.hosting == account.hosting and acc.login == account.login and acc.url == account.url:
                break
            index += 1

        msg = QtWidgets.QMessageBox(self)
        msg.setText(get_str('authorized_successfully'))

        if hosting.value[0].need_to_pass_channel_after_login():
            try:
                if hosting.value[0].validate_url_by_account(account.destination, account) is False:
                    msg = QtWidgets.QMessageBox(self)
                    msg.setText(f'{get_str("failed_account_validation")}: {account.destination}')
                    self.event_service.add_event(Event(f'{get_str("failed_account_validation")}: {account.destination}'))
                    msg.exec_()
                    return
            except:
                msg.exec_()
                log_error(traceback.format_exc())
                self.event_service.add_event(Event(f'{get_str("failed_account_validation")}: {account.url}'))
                self.add_button.stop_animation()
                return
        msg.exec_()

        QueueMediaService().add_reauthorized_account_from_accounts_page(acc_temp, account)

        button = self.sender()
        row = self.indexAt(button.pos()).row()
        self.item(row, 1).setText(account.url if account.url is not None else account.login)
        self.accounts[row] = account
        self.state_service.save_accounts(self.accounts)

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            pos = self.horizontalScrollBar().sliderPosition()
            self.removeRow(row)
            self.accounts.pop(row)
            self.state_service.save_accounts(self.accounts)
            self.horizontalScrollBar().setSliderPosition(pos)

    change = True

    def section_resized(self, index, width):
        if self.change:
            coef_x = self.parent().width() / 950
            self.state_service.save_column_row('accounts', index, int(width / coef_x))

    def resizeEvent(self, event):
        self.change = False
        coef_x = self.parent().width() / 950

        if self.state_service.column_row('accounts', 0) is None or self.state_service.column_row('accounts', 1) is None or self.state_service.column_row('accounts', 2) is None or self.state_service.column_row('accounts', 3) is None:
            column_width = int(950 / 4)

            if self.state_service.column_row('accounts', 0) is None:
                self.state_service.save_column_row('accounts', 0, column_width)
            if self.state_service.column_row('accounts', 1) is None:
                self.state_service.save_column_row('accounts', 1, column_width)
            if self.state_service.column_row('accounts', 2) is None:
                self.state_service.save_column_row('accounts', 2, column_width)
            if self.state_service.column_row('accounts', 3) is None:
                self.state_service.save_column_row('accounts', 3, column_width)

        width_0 = int(self.state_service.column_row('accounts', 0) * coef_x)
        width_1 = int(self.state_service.column_row('accounts', 1) * coef_x)
        width_2 = int(self.state_service.column_row('accounts', 2) * coef_x)
        width_3 = int(self.state_service.column_row('accounts', 3) * coef_x)

        self.setColumnWidth(0, width_0)
        self.setColumnWidth(1, width_1)
        self.setColumnWidth(2, width_2)
        self.setColumnWidth(3, width_3)

        self.change = True

        return super(AccountsPageWidget, self).resizeEvent(event)
