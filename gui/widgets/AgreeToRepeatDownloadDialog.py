from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QSpinBox, QGridLayout, QComboBox, QMessageBox)

from gui.widgets.ChooseAccountsForUploadingForm import ChooseAccountsForUploadingForm
from gui.widgets.ChooseChannelForm import ChooseChannelForm
from model.Hosting import Hosting
from service.LocalizationService import *


class AgreeToRepeatDownloadDialog(QDialog):

    is_agree = False

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(get_str('agree_to_repeat'))
        self.resize(450, 120)

        layout = QGridLayout()

        video_has_been_loaded_label = QLabel(get_str("video_has_been_loaded"))
        layout.addWidget(video_has_been_loaded_label, 1, 0)

        yes_button = QPushButton(get_str('yes'))
        yes_button.clicked.connect(self.on_yes)
        yes_button.setMaximumWidth(100)
        layout.addWidget(yes_button, 2, 0)

        no_button = QPushButton(get_str('no'))
        no_button.clicked.connect(self.on_no)
        no_button.setMaximumWidth(100)
        layout.addWidget(no_button, 2, 1)
        layout.setRowMinimumHeight(2, 75)

        self.setLayout(layout)

    def on_no(self):
        self.close()

    def on_yes(self):
        self.is_agree = True
        self.close()
