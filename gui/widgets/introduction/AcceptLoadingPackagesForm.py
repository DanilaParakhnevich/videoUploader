from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QGridLayout)


class AcceptLoadingPackagesForm(QDialog):

    accept = False

    def __init__(self, failed):
        super().__init__()
        if failed:
            self.setWindowTitle('Произошел сбой, необходимо возобновить установку пакетов')
        else:
            self.setWindowTitle('Для продолжения необходимо установить пакеты')
        self.resize(500, 120)

        self.gridLayout = QGridLayout(self)

        self.yes_button = QPushButton()
        self.yes_button.setObjectName("yes_button")
        self.yes_button.setMaximumWidth(200)
        self.yes_button.setText('Продолжить')
        self.yes_button.clicked.connect(self.yes)

        self.no_button = QPushButton()
        self.no_button.setObjectName("no_button")
        self.no_button.setMaximumWidth(200)
        self.no_button.setText('Отмена')
        self.no_button.clicked.connect(self.no)

        self.gridLayout.addWidget(self.yes_button, 2, 1)
        self.gridLayout.addWidget(self.no_button, 2, 2)

    def yes(self):
        self.accept = True
        self.close()

    def no(self):
        self.close()
