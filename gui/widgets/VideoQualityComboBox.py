from PyQt5 import QtWidgets
from service.LocalizationService import *

class VideoQualityComboBox(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

        self.insertItem(0, get_str('bestvideo'), 'bestvideo')
        self.insertItem(1, get_str('worstvideo'), 'worstvideo')

        self.setCurrentIndex(0)
