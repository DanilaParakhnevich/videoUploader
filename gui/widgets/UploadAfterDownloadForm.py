from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QSpinBox, QGridLayout, QComboBox)


class UploadAfterDownloadForm(QDialog):

	upload_flag = False
	upload_interval = None
	upload_interval_type = None

	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowTitle(f'Выгружать видео после скачивания?')
		self.resize(500, 120)

		layout = QGridLayout()

		label_name = QLabel('<font size="4"> Интервал </font>')
		self.time_edit = QSpinBox()
		layout.addWidget(label_name, 0, 0)
		layout.addWidget(self.time_edit, 0, 1)
		self.time_type_edit = QComboBox()

		self.time_type_edit.addItem('Минуты')
		self.time_type_edit.addItem('Часы')
		self.time_type_edit.addItem('Дни')
		self.time_type_edit.addItem('Месяца')

		self.time_type_edit.setCurrentIndex(0)

		layout.addWidget(self.time_type_edit, 0, 2)

		yes_button = QPushButton('Да')
		yes_button.clicked.connect(self.on_yes)
		layout.addWidget(yes_button, 2, 0, 1, 2)
		layout.setRowMinimumHeight(2, 75)

		no_button = QPushButton('Нет')
		no_button.clicked.connect(self.on_no)
		layout.addWidget(no_button, 2, 1, 1, 2)
		layout.setRowMinimumHeight(2, 75)

		self.setLayout(layout)

	def on_no(self):
		self.upload_flag = False
		self.close()

	def on_yes(self):
		self.upload_flag = True
		self.upload_interval = int(self.time_edit.text())
		self.upload_interval_type = self.time_type_edit.currentIndex()
		self.close()
