from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from gui.widgets.AccountsListWidget import AccountsListWidget
from gui.widgets.EventsListWidget import EventsListWidget
from service.LocalizationService import *


class EventsListForm(QDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.state_service = StateService()
        self.setWindowTitle(get_str('events'))
        self.resize(500, 120)

        layout = QGridLayout()

        self.events_list_widget = EventsListWidget(self)

        layout.addWidget(self.events_list_widget, 0, 0)

        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
