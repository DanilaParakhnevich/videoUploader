from PyQt5 import QtCore, QtWidgets

from model.Hosting import Hosting
from service.LocalizationService import *


class AccountsPageWidget(QtWidgets.QTableWidget):
    comboBox = QtWidgets.QComboBox()

    state_service = StateService()

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
        add_button = QtWidgets.QPushButton(central_widget)
        add_button.setObjectName("add_button")
        horizontal_layout.addWidget(add_button)
        horizontal_layout.setAlignment(QtCore.Qt.AlignBottom)

        add_button.clicked.connect(self.on_add)

        _translate = QtCore.QCoreApplication.translate
        item = self.horizontalHeaderItem(0)
        item.setText(_translate("BuharVideoUploader", get_str('videohosting')))
        item = self.horizontalHeaderItem(1)
        item.setText(_translate("BuharVideoUploader", get_str('login')))
        item = self.horizontalHeaderItem(2)
        item.setText(_translate("BuharVideoUploader", get_str('delete')))
        add_button.setText(_translate("BuharVideoUploader", get_str('add')))

        for account in self.accounts:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(account.hosting)
            item2 = QtWidgets.QTableWidgetItem(account.login)

            input_position = self.rowCount() - 1

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')
            self.setCellWidget(input_position, 2, btn)

            btn.clicked.connect(self.on_delete_row)

            self.setItem(input_position, 0, item1)
            self.setItem(input_position, 1, item2)

    def on_add(self):
        hosting = Hosting[self.comboBox.currentText()]

        account = hosting.value[0].show_login_dialog(hosting, self.parentWidget())
        if account is not None:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(self.comboBox.currentText())
            item2 = QtWidgets.QTableWidgetItem(account.login)

            input_position = self.rowCount() - 1

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')
            self.setCellWidget(input_position, 2, btn)

            btn.clicked.connect(self.on_delete_row)

            self.setItem(input_position, 0, item1)
            self.setItem(input_position, 1, item2)

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            self.removeRow(row)
            self.accounts.pop(row)
            self.state_service.save_accounts(self.accounts)
