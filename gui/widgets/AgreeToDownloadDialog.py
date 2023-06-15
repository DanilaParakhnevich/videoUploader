from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QSpinBox, QGridLayout, QComboBox, QMessageBox)

from gui.widgets.ChooseAccountsForUploadingForm import ChooseAccountsForUploadingForm
from gui.widgets.ChooseChannelForm import ChooseChannelForm
from model.Hosting import Hosting
from service.LocalizationService import *


class AgreeToDownloadDialog(QDialog):

    is_agree = False

    def __init__(self, parent, available_video_quality):
        super().__init__(parent)
        self.setWindowTitle(get_str('agree_to_download'))
        self.resize(450, 120)

        layout = QGridLayout()

        if available_video_quality is not None:
            available_video_label = QLabel(f'{get_str("only_available")} {available_video_quality}p')
            layout.addWidget(available_video_label, 1, 0)
        else:
            available_video_label = QLabel(f'{get_str("no_available")}')
            layout.addWidget(available_video_label, 1, 0)

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
