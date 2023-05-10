from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)

from service.LocalizationService import *


class SpecialSourceForm(QDialog):

	passed = False

	def __init__(self, parent, hosting, service, account):
		super().__init__(parent)
		self.setWindowTitle(f'{get_str("choose_source_for")} {hosting}')
		self.resize(500, 120)

		layout = QGridLayout()

		label_name = QLabel(f'<font size="4"> {get_str("source")} </font>')
		self.source_edit = QLineEdit()
		self.source_edit.setPlaceholderText(get_str('choose_source_for_upload'))
		layout.addWidget(label_name, 0, 0)
		layout.addWidget(self.source_edit, 0, 1)

		button_check = QPushButton(get_str('check'))
		button_check.clicked.connect(self.exit)
		layout.addWidget(button_check, 2, 0, 1, 2)
		layout.setRowMinimumHeight(2, 75)

		self.setLayout(layout)
		self.service = service
		self.account = account

	def exit(self):
		try:
			self.service.validate_special_source(self.account, self.source_edit.text())
			self.passed = True
			self.close()
		except:
			msg = QMessageBox()
			msg.setText(get_str('upload_source_not_found'))
			msg.exec_()
