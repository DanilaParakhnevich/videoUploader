from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QComboBox)

from gui.widgets.AccountsListWidget import AccountsListWidget
from gui.widgets.VideoListWidget import VideoListWidget
from service.LocalizationService import *


class ChooseLoadedVideoForm(QDialog):
    video_dirs = list()
    passed = False

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.state_service = StateService()
        self.setWindowTitle(get_str('choose_video_for_uploading'))
        self.resize(500, 120)

        layout = QGridLayout()

        self.video_list_widget = VideoListWidget(self, self.state_service.get_download_queue_media())

        layout.addWidget(self.video_list_widget, 0, 0)

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose_video)
        layout.addWidget(button_choose, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)

    def choose_video(self):
        for i in range(0, self.video_list_widget.rowCount()):
            if self.video_list_widget.item(i, 2).checkState() != 0:
                self.video_dirs.append(self.video_list_widget.item(i, 1).text())
        self.passed = True
        self.close()
