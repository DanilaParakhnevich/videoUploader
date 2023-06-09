from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QLineEdit, QMessageBox)

from service.LocalizationService import *


class ShowErrorDialog(QDialog):

    def __init__(self, parent: QWidget, error: str):
        super().__init__(parent)
        self.setWindowTitle(get_str('upload_error'))
        self.resize(500, 120)

        layout = QGridLayout()

        self.label = QLabel()
        self.label.setText(error)

        layout.addWidget(self.label, 0, 0)

        button = QPushButton(get_str('ok'))
        button.clicked.connect(self.on_input)
        layout.addWidget(button, 1, 0)
        layout.setRowMinimumHeight(3, 75)
        self.setLayout(layout)

    def on_input(self):
        self.close()