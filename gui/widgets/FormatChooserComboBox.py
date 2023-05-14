from PyQt5 import QtWidgets
from service.LocalizationService import *


class FormatChooserComboBox(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

        self.addItem(get_str('video_and_audio'), None)
        self.addItem(get_str('not_merge_video_and_audio'), 'NOT_MERGE')
        self.addItem(get_str('video'), 'VIDEO')
        self.addItem(get_str('audio'), 'AUDIO')

        self.setCurrentIndex(0)
