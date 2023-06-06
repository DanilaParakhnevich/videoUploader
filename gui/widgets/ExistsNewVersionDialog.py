from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from service.LocalizationService import *


# Этот QDialog предназначен для отображения наличия новой версии
class ExistsNewVersionDialog(QDialog):
    account = None

    def __init__(self, version: str):
        super().__init__()
        self.setWindowTitle(get_str('new_version'))
        self.resize(500, 120)

        layout = QGridLayout()

        new_version_label = QLabel('new_version_label')
        new_version_label.setText(f'{get_str("new_version")}: {version}')

        ok_button = QPushButton('ok_button')
        ok_button.clicked.connect(self.ok)
        ok_button.setText(get_str('ok'))

        layout.addWidget(new_version_label, 0, 0)
        layout.addWidget(ok_button, 0, 1)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)

    def ok(self):
        self.close()
