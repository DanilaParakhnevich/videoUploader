from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QSpinBox, QGridLayout, QComboBox)
from service.LocalizationService import *


class ChooseIntervalForm(QDialog):

    upload_interval = None
    upload_interval_type = None
    passed = False

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(get_str('choose_intervals'))
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(f'<font size="4"> {get_str("interval")} </font>')
        self.time_edit = QSpinBox()
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.time_edit, 0, 1)
        self.time_type_edit = QComboBox()

        self.time_type_edit.addItem(get_str('minutes'))
        self.time_type_edit.addItem(get_str('hours'))
        self.time_type_edit.addItem(get_str('days'))
        self.time_type_edit.addItem(get_str('months'))

        self.time_type_edit.setCurrentIndex(0)

        layout.addWidget(self.time_type_edit, 0, 2)

        ok_button = QPushButton(get_str('choose'))
        ok_button.clicked.connect(self.ok)
        layout.addWidget(ok_button, 2, 0, 1, 2)

        self.setLayout(layout)

    def ok(self):
        self.upload_interval = int(self.time_edit.text())
        self.upload_interval_type = self.time_type_edit.currentIndex()
        self.passed = True
        self.close()
