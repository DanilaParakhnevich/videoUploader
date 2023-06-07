from PyQt5 import QtWidgets


class ExtensionChooserComboBox(QtWidgets.QComboBox):

    def __init__(self, parent):
        super().__init__(parent)

        self.addItem('3gp', '3gp')
        self.addItem('aac', 'aac')
        self.addItem('flv', 'flv')
        self.addItem('m4a', 'm4a')
        self.addItem('mp3', 'mp3')
        self.addItem('mp4', 'mp4')
        self.addItem('ogg', 'ogg')
        self.addItem('wav', 'wav')
        self.addItem('webm', 'webm')

        self.setCurrentIndex(0)
