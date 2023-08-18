from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QLineEdit, QMessageBox)

from model.Hosting import Hosting
from service.LocalizationService import *


class TypeUrlForm(QDialog):
    url = None
    passed = False

    def __init__(self, parent: QWidget, hosting: Hosting, title: str = get_str("type_url_for")):
        super().__init__(parent)
        self.setWindowTitle(f'{title} {hosting.name}')
        self.setFixedSize(500, 120)

        layout = QGridLayout()

        self.edit = QLineEdit()

        layout.addWidget(self.edit, 0, 0)

        button = QPushButton(get_str('choose'))
        button.clicked.connect(self.on_input)
        layout.addWidget(button, 0, 1)
        layout.setRowMinimumHeight(3, 75)

        self.hosting = hosting
        self.setLayout(layout)
        self.state_service = StateService()

    def on_input(self):
        self.url = self.edit.text()

        if self.hosting.value[0].validate_page(self.url) != 1:
            msg = QMessageBox()
            msg.setText(get_str('bad_link'))
            msg.exec_()
        else:
            self.passed = True
            self.close()
