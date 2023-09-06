from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QSpinBox, QGridLayout, QComboBox)
from service.LocalizationService import *


class ChooseIntervalForm(QDialog):

    upload_interval = None
    upload_interval_type = None
    upload_minutes = None
    upload_hours = None
    yes = False
    passed = False

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(get_str('choose_intervals'))
        self.resize(500, 120)

        layout = QGridLayout()

        upload_label_name = QLabel(f'<font size="4"> {get_str("interval")} </font>')
        self.upload_time_edit = QSpinBox()
        layout.addWidget(upload_label_name, 1, 0)
        layout.addWidget(self.upload_time_edit, 1, 1)
        self.upload_time_type_edit = QComboBox()

        self.upload_time_type_edit.addItem(get_str('minutes'))
        self.upload_time_type_edit.addItem(get_str('hours'))
        self.upload_time_type_edit.addItem(get_str('days'))
        self.upload_time_type_edit.addItem(get_str('months'))

        self.upload_time_type_edit.setCurrentIndex(0)

        layout.addWidget(self.upload_time_type_edit, 1, 2)

        upload_time_label = QLabel(f'<font size="4"> {get_str("first_upload_time")} </font>')

        self.upload_hours_edit = QSpinBox()
        self.upload_hours_edit.setMinimum(0)
        self.upload_hours_edit.setMaximum(24)
        self.upload_minutes_edit = QSpinBox()
        self.upload_minutes_edit.setMinimum(0)
        self.upload_minutes_edit.setMaximum(60)

        layout.addWidget(upload_time_label, 2, 0)
        layout.addWidget(self.upload_hours_edit, 2, 1)
        layout.addWidget(self.upload_minutes_edit, 2, 2)

        ok_button = QPushButton(get_str('choose'))
        ok_button.clicked.connect(self.ok)
        layout.addWidget(ok_button, 3, 0, 1, 2)

        self.setLayout(layout)

    def ok(self):
        self.upload_minutes = int(self.upload_minutes_edit.text())
        self.upload_hours = int(self.upload_hours_edit.text())

        self.upload_interval = int(self.upload_time_edit.text())
        self.upload_interval_type = self.upload_time_type_edit.currentIndex()

        self.yes = True
        self.passed = True
        self.close()
