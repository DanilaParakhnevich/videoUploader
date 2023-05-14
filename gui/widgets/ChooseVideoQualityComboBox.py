from PyQt5 import QtWidgets


class ChooseVideoQualityComboBox(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

        self.addItem('144p', '144')
        self.addItem('240p', '240')
        self.addItem('360p', '360')
        self.addItem('480p', '480')
        self.addItem('720p', '720')
        self.addItem('1080p', '1080')
        self.addItem('1440p', '1440')
        self.addItem('2160p', '2160')

        self.setCurrentIndex(0)
