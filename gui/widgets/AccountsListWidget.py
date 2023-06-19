from PyQt5 import QtCore, QtWidgets

from service.LocalizationService import get_str


class AccountsListWidget(QtWidgets.QTableWidget):

    comboBox = QtWidgets.QComboBox()

    def __init__(self, parent, account_list):
        super(AccountsListWidget, self).__init__(parent)
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
        self.horizontalHeader().sectionClicked.connect(self.section_clicked)
        self.horizontalHeader().setDefaultSectionSize(155)

        for account in account_list:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(account.url if account.url is not None else account.login)
            item2 = QtWidgets.QTableWidgetItem(account.hosting)

            item3 = QtWidgets.QTableWidgetItem()
            item3.setFlags(QtCore.Qt.ItemIsUserCheckable |
                           QtCore.Qt.ItemIsEnabled)
            item3.setCheckState(QtCore.Qt.Unchecked)

            self.setItem(self.rowCount() - 1, 0, item1)
            self.setItem(self.rowCount() - 1, 1, item2)
            self.setItem(self.rowCount() - 1, 2, item3)

        item = self.horizontalHeaderItem(0)
        item.setText(get_str("login"))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str("videohosting"))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str("upload"))

    def section_clicked(self, index):
        if index == 2:

            if self.rowCount() > 0:
                to_set = QtCore.Qt.Checked if self.item(0, 2).checkState() == 0 else 0

            for index in range(0, self.rowCount()):
                self.item(index, 2).setCheckState(to_set)