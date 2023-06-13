from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from gui.widgets.AccountsListWidget import AccountsListWidget
from gui.widgets.EventsListWidget import EventsListWidget
from service.LocalizationService import *


class EventsListForm(QDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.state_service = StateService()
        self.setWindowTitle(get_str('events'))
        width = self.state_service.get_events_column_width()
        height = self.state_service.get_events_list_height()
        self.resize(int(width * 500 / 145), height)

        layout = QGridLayout()

        self.events_list_widget = EventsListWidget(self)

        layout.addWidget(self.events_list_widget, 0, 0)

        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)

    def resizeEvent(self, event):
        self.events_list_widget.setColumnWidth(0, int(self.width() * 145/500))
        self.events_list_widget.setColumnWidth(1, int(self.width() * 145/500))
        self.events_list_widget.setColumnWidth(2, int(self.width() * 145/500))
        self.state_service.save_events_list_height(self.height())
        return super(EventsListForm, self).resizeEvent(event)
