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
        self.change = False
        self.resize(int(width * 500 / 145), height)

        layout = QGridLayout()

        self.events_list_widget = EventsListWidget(self)

        layout.addWidget(self.events_list_widget, 0, 0)

        layout.setRowMinimumHeight(3, 75)
        self.events_list_widget.horizontalHeader().sectionResized.connect(self.section_resized)

        self.setLayout(layout)

    def section_resized(self, index, width):
        if self.change:
            coef_x = self.parent().width() / 500
            self.state_service.save_column_row('events', index, int(width / coef_x))

    def resizeEvent(self, event):
        coef_x = self.parent().width() / 500
        self.events_list_widget.setColumnWidth(0, int((self.state_service.column_row('events', 0) if self.state_service.column_row('events', 0) != None else 145) * coef_x))
        self.events_list_widget.setColumnWidth(1, int((self.state_service.column_row('events', 1) if self.state_service.column_row('events', 1) != None else 145) * coef_x))
        self.events_list_widget.setColumnWidth(2, int((self.state_service.column_row('events', 2) if self.state_service.column_row('events', 2) != None else 145) * coef_x))
        self.state_service.save_events_list_height(self.height())

        self.change = True

        return super(EventsListForm, self).resizeEvent(event)
