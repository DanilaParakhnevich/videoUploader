from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from service.StateService import StateService
from service.LocalizationService import *
from model.Hosting import Hosting


class ChooseHostingForm(QDialog):
    hosting = None

    def __init__(self, parent: QWidget, choose_hosting_text=get_str('choose_hosting')):
        super().__init__(parent)
        self.setWindowTitle(choose_hosting_text)
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(f'<font size="4"> {choose_hosting_text} </font>')
        self.combo_box = QComboBox()
        self.combo_box.setPlaceholderText(choose_hosting_text)

        for hosting in Hosting:
            if hosting.name is not 'DTube':
                self.combo_box.addItem(hosting.name, hosting)

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.combo_box, 0, 1)

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose_hosting)
        layout.addWidget(button_choose, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()

    def choose_hosting(self):
        self.hosting = self.combo_box.currentData()
        self.close()
