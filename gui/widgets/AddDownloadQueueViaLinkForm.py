from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QMessageBox, QComboBox, QGridLayout)

from model.Hosting import Hosting
from service.LocalizationService import *
from gui.widgets.ChooseAccountForm import ChooseAccountForm
from gui.widgets.ChooseLinkForm import ChooseLinkForm


class AddDownloadQueueViaLinkForm(QDialog):

    account = None
    hosting = None
    link = None
    passed = False

    def __init__(self, parent):

        super().__init__(parent)
        self.setWindowTitle(get_str('adding_video_via_url'))
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel(f'<font size="4"> {get_str("videohosting")} </font>')
        self.combo_box = QComboBox()

        for hosting in Hosting:
            self.combo_box.addItem(hosting.name, hosting)

        self.combo_box.setCurrentIndex(0)

        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.combo_box, 0, 1)

        button_choose = QPushButton(get_str('choose'))
        button_choose.clicked.connect(self.choose)
        layout.addWidget(button_choose, 3, 0, 1, 2)
        layout.setRowMinimumHeight(3, 75)

        self.setLayout(layout)
        self.state_service = StateService()

    def choose(self):
        accounts = self.state_service.get_accounts_by_hosting(self.combo_box.currentText())

        if len(accounts) == 0 and Hosting[self.combo_box.currentText()].value[1]:
            msg = QMessageBox()
            msg.setText(get_str('need_authorize'))
            msg.exec_()
            return
        else:
            form = ChooseAccountForm(parent=self.parentWidget(),
                                     accounts=accounts)
            form.exec_()

            if form.account is None and Hosting[self.combo_box.currentText()].value[1]:
                return

        self.account = form.account

        form = ChooseLinkForm(parent=self.parentWidget(), hosting=self.combo_box.currentText())
        form.exec_()

        if form.passed is False:
            return

        self.link = form.link_edit.text()
        self.hosting = self.combo_box.currentText()
        self.passed = True
        self.close()
