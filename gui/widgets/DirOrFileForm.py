from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QLabel, QGridLayout, QFileDialog, QMessageBox)

from service.LocalizationService import *


class DirOrFileForm(QDialog):

    file_need = None
    passed = False

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle(get_str('choose_the_dir_or_file'))
        self.setFixedSize(500, 120)

        self.gridLayout = QGridLayout(self)

        self.file_button = QPushButton()
        self.file_button.setObjectName("file_need")
        self.file_button.setMaximumWidth(200)
        self.file_button.setText(get_str('file_need'))
        self.file_button.clicked.connect(self.file)

        self.dir_button = QPushButton()
        self.dir_button.setObjectName("dir_need")
        self.dir_button.setMaximumWidth(200)
        self.dir_button.setText(get_str('dir_need'))
        self.dir_button.clicked.connect(self.dir)

        self.gridLayout.addWidget(self.file_button, 2, 1)
        self.gridLayout.addWidget(self.dir_button, 2, 2)

    def file(self):
        self.file_need = True
        self.passed = True
        self.close()

    def dir(self):
        self.file_need = False
        self.passed = True
        self.close()
