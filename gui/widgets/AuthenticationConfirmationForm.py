from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QLineEdit, QGridLayout)
from service.LocalizationService import *


# Эта форма предназначена для автоматизированной авторизации и используется в реализациях метода login наследников
# VideohostingService
class AuthenticationConfirmationForm(QDialog):

	passed = False

	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowTitle(get_str('authentication'))
		self.resize(500, 120)

		layout = QGridLayout()

		label_name = QLabel(f'<font size="4"> {get_str("code")} </font>')
		self.code_edit = QLineEdit()
		self.code_edit.setPlaceholderText(get_str('enter_auth_code'))
		layout.addWidget(label_name, 0, 0)
		layout.addWidget(self.code_edit, 0, 1)

		button_check = QPushButton(get_str('check'))
		button_check.clicked.connect(self.exit)
		layout.addWidget(button_check, 2, 0, 1, 2)
		layout.setRowMinimumHeight(2, 75)

		self.setLayout(layout)

	def exit(self):
		self.passed = True
		self.close()
