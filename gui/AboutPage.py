
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel

from gui.widgets.ClickableLabel import ClickableLabel
from service.LocalizationService import *
from service.VersionService import VersionService


class AboutPage(QtWidgets.QDialog):
    state_service = StateService()

    def __init__(self, central_widget):

        super(AboutPage, self).__init__(central_widget)
        self.setFixedSize(500, 400)
        self.setObjectName("AboutPage")

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(-100)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.about_link_label = QLabel()
        self.about_link_label.setText(get_str('link_text'))
        self.link_label = ClickableLabel(get_str('link_value'), False)

        self.gridLayout.addWidget(self.about_link_label, 0, 0)
        self.gridLayout.addWidget(self.link_label, 0, 1)

        self.about_email_label = QLabel()
        self.about_email_label.setText(get_str('email_text'))
        self.email_label = ClickableLabel(get_str('email_value'), True)

        self.gridLayout.addWidget(self.about_email_label, 1, 0)
        self.gridLayout.addWidget(self.email_label, 1, 1)

        self.text_info_label = QLabel()
        self.text_info_label.setText(get_str('text_info_text'))
        self.text_label = QLabel()
        self.text_label.setText(get_str('text_info_value').replace('{version}', VersionService().get_current_version()))

        self.gridLayout.addWidget(self.text_info_label, 2, 0)
        self.gridLayout.addWidget(self.text_label, 2, 1)

        self.retranslate_ui()

    def parse_string(self, string: str) -> str:
        new_string = ""

        for letter_index in range(len(string)):

            if letter_index % 33 == 0 and letter_index != 0:
                new_string += "\n"
            else:
                new_string += string[letter_index]

        return new_string

    def retranslate_ui(self):
        self.setWindowTitle(get_str('about_page'))
