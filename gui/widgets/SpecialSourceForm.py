from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)


class SpecialSourceForm(QDialog):

	passed = False

	def __init__(self, parent, hosting, service, account):
		super().__init__(parent)
		self.setWindowTitle(f'Выбор источника выгрузки для {hosting}')
		self.resize(500, 120)

		layout = QGridLayout()

		label_name = QLabel('<font size="4"> Источник </font>')
		self.source_edit = QLineEdit()
		self.source_edit.setPlaceholderText('Выберите источник для выгрузки')
		layout.addWidget(label_name, 0, 0)
		layout.addWidget(self.source_edit, 0, 1)

		button_check = QPushButton('Проверка')
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
			msg.setText('Источник выгрузки не найден')
			msg.exec_()
