from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QLineEdit, QGridLayout)


class AuthenticationConfirmationForm(QDialog):
	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowTitle('Аутентификация')
		self.resize(500, 120)

		layout = QGridLayout()

		label_name = QLabel('<font size="4"> Код </font>')
		self.code_edit = QLineEdit()
		self.code_edit.setPlaceholderText('Введите код для аутентификации')
		layout.addWidget(label_name, 0, 0)
		layout.addWidget(self.code_edit, 0, 1)

		button_check = QPushButton('Проверка')
		button_check.clicked.connect(self.exit)
		layout.addWidget(button_check, 2, 0, 1, 2)
		layout.setRowMinimumHeight(2, 75)

		self.setLayout(layout)

	def close(self) -> bool:
		return super().close()

	def exit(self):
		self.close()
