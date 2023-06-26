import traceback

from PyQt5.QtWidgets import (QDialog, QPushButton, QGridLayout, QLabel, QLineEdit)

from service.LocalizationService import *
from service.LoggingService import log_error
from service.MailService import MailService

class EnterLicenseKeyForm(QDialog):
    license = None
    mail = None

    def __init__(self):
        super().__init__()
        self.passed = False
        self.setFixedSize(400, 200)
        self.setWindowTitle(get_str('enter_license'))
        self.layout = QGridLayout()

        self.license_edit = QLineEdit()
        self.license_edit.setPlaceholderText(get_str('print_license'))
        self.layout.addWidget(self.license_edit, 0, 0)

        self.mail_edit = QLineEdit()
        self.mail_edit.setPlaceholderText(get_str('enter_mail'))
        self.layout.addWidget(self.mail_edit, 1, 0)

        self.button_on_send_log = QPushButton(get_str('report_bug'))
        self.button_on_send_log.clicked.connect(self.on_send_log)
        self.layout.addWidget(self.button_on_send_log, 2, 1)

        button = QPushButton(get_str('activate'))
        button.clicked.connect(self.ok)
        self.layout.addWidget(button, 2, 0)
        self.layout.setRowMinimumHeight(3, 75)

        send_successfully = QLabel()
        self.layout.addWidget(send_successfully, 3, 0)

        self.setLayout(self.layout)

    def on_send_log(self):
        try:
            MailService().send_log()
            self.button_on_send_log.setDisabled(True)

            send_successfully = QLabel()
            send_successfully.setText(get_str('send_successfully'))
            self.layout.addWidget(send_successfully, 3, 0)
        except:
            log_error('Ошибка при отправке лога')
            log_error(traceback.format_exc())
            send_successfully = QLabel()
            send_successfully.setText(get_str('send_failed'))
            self.layout.addWidget(send_successfully, 3, 0)

    def ok(self):
        self.license = self.license_edit.text()
        self.mail = self.mail_edit.text()
        self.passed = True
        self.close()
