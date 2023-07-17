import traceback

from PyQt5.QtWidgets import (QDialog, QPushButton, QGridLayout, QLabel, QLineEdit)

from gui.widgets.ClickableLabel import ClickableLabel
from service.LocalizationService import *
from service.LoggingService import log_error
from service.MailService import MailService

class EnterLicenseKeyForm(QDialog):
    license = None
    mail = None

    def __init__(self):
        super().__init__()
        self.passed = False
        self.setFixedSize(500, 400)
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

        mail_label = QLabel()
        mail_label.setText(get_str('email_text'))
        self.layout.addWidget(mail_label, 3, 0)

        mail = ClickableLabel(get_str('email_value'), True)
        self.layout.addWidget(mail, 3, 1)

        site_label = QLabel()
        site_label.setText(get_str('link_text'))
        self.layout.addWidget(site_label, 4, 0)

        site = ClickableLabel(get_str('link_value'), False)
        self.layout.addWidget(site, 4, 1)

        about_label = QLabel()
        about_label.setText(get_str('text_info_text'))

        self.layout.addWidget(about_label, 5, 0)

        about = QLabel()
        about.setText(get_str('text_info_value'))

        self.layout.addWidget(about, 5, 1)

        send_successfully = QLabel()
        self.layout.addWidget(send_successfully, 6, 0)

        self.setLayout(self.layout)

    def parse_string(self, string: str) -> str:
        new_string = ""

        index = 0

        for letter_index in range(len(string)):

            if index % 33 == 0 and index != 0:
                if string[letter_index] != ' ':
                    new_string += f"\n{string[letter_index]}"
                    index += 1
            else:
                new_string += string[letter_index]

            index += 1

            if index > 33:
                index = 0

        return new_string

    def on_send_log(self):
        try:
            MailService().send_log()
            self.button_on_send_log.setDisabled(True)

            send_successfully = QLabel()
            send_successfully.setText(get_str('send_successfully'))
            self.layout.addWidget(send_successfully, 6, 0)
        except:
            log_error('Ошибка при отправке лога')
            log_error(traceback.format_exc())
            send_successfully = QLabel()
            send_successfully.setText(get_str('send_failed'))
            self.layout.addWidget(send_successfully, 6, 0)

    def ok(self):
        self.license = self.license_edit.text()
        self.mail = self.mail_edit.text()
        self.passed = True
        self.close()
