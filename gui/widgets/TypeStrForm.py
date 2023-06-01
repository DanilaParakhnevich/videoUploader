from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QGridLayout, QTextEdit, QLabel, QSizePolicy)

from service.LocalizationService import *


class TypeStrForm(QDialog):
    str = None
    passed = False

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if a0.type() == 99:
            self.state_service.save_type_url_form_size(self.size())
        super().changeEvent(a0)

    def __init__(self, parent: QWidget, label: str, current_text: str = ''):
        super().__init__(parent)
        self.state_service = StateService()
        self.setWindowTitle(label)
        self.resize(self.state_service.get_type_url_form_size())
        layout = QGridLayout()

        self.edit = QTextEdit()
        self.edit.setText(current_text)
        self.edit.textChanged.connect(self.on_change)
        self.edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.edit, 0, 0)

        button = QPushButton(get_str('choose'))
        button.clicked.connect(self.ok)
        layout.addWidget(button, 0, 1)
        layout.setRowMinimumHeight(3, 75)

        self.counter = QLabel()
        self.counter.setText(len(current_text).__str__() if current_text is not None else "0")

        layout.addWidget(self.counter, 1, 0)

        self.setLayout(layout)

    def on_change(self):
        self.counter.setText(len(self.edit.toPlainText()).__str__())

    def ok(self):
        self.str = self.edit.toPlainText()
        self.passed = True
        self.close()
