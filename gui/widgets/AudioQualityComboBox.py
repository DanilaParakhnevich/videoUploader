from PyQt5 import QtWidgets
from service.LocalizationService import *

class AudioQualityComboBox(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

        self.insertItem(0, get_str('bestaudio'), 'bestaudio')
        self.insertItem(1, get_str('worstaudio'), 'worstaudio')

        self.setCurrentIndex(0)
