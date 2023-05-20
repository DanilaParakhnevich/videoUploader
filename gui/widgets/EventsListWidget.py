from PyQt5 import QtCore, QtWidgets

from service.LocalizationService import get_str
from service.StateService import StateService


class EventsListWidget(QtWidgets.QTableWidget):

    state_service = StateService()

    def __init__(self, parent):
        super(EventsListWidget, self).__init__(parent)
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
        self.horizontalHeader().setDefaultSectionSize(155)
        self.events = self.state_service.get_events()

        for event in self.events:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(event.msg)
            item2 = QtWidgets.QTableWidgetItem(str(event.date))

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')

            btn.clicked.connect(self.on_delete_row)

            self.setItem(self.rowCount() - 1, 0, item1)
            self.setItem(self.rowCount() - 1, 1, item2)
            self.setCellWidget(self.rowCount() - 1, 2, btn)

        item = self.horizontalHeaderItem(0)
        item.setText(get_str("event"))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str("date"))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str("delete"))

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            self.removeRow(row)
            self.events.pop(row)
            self.state_service.save_events(self.events)
