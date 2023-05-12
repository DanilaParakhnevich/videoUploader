from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QLineEdit)

from service.LocalizationService import *


class TypeStrForm(QDialog):
    str = None
    passed = False

    def __init__(self, parent: QWidget, label: str, current_text: str = ''):
        super().__init__(parent)
        self.setWindowTitle(label)
        self.resize(500, 120)

        layout = QGridLayout()

        self.edit = QLineEdit()
        self.edit.setText(current_text)

        layout.addWidget(self.edit, 0, 0)

        button = QPushButton(get_str('choose'))
        button.clicked.connect(self.ok)
        layout.addWidget(button, 0, 1)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()

    def ok(self):
        self.str = self.edit.text()
        self.passed = True
        self.close()
