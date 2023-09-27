from datetime import datetime, timedelta

from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QSpinBox, QGridLayout, QComboBox, QMessageBox)

from gui.widgets.ChooseAccountsForUploadingForm import ChooseAccountsForUploadingForm
from gui.widgets.ChooseChannelForm import ChooseChannelForm
from model.Hosting import Hosting
from service.LocalizationService import *


class UploadAfterDownloadForm(QDialog):
	upload_flag = False
	upload_interval = None
	upload_interval_type = None
	upload_targets = None
	first_upload_date = None
	load_interval = 0
	load_interval_type = 0
	passed = False

	def __init__(self, parent, need_interval: bool = True, video_size: str = None):
		super().__init__(parent)
		self.setWindowTitle(get_str('upload_video_after_download'))
		self.resize(450, 120)

		layout = QGridLayout()
		if need_interval:
			self.resize(500, 120)
			load_label_name = QLabel(f'<font size="4"> {get_str("load_interval")} </font>')
			self.load_time_edit = QSpinBox()
			layout.addWidget(load_label_name, 0, 0)
			layout.addWidget(self.load_time_edit, 0, 1)
			self.load_time_type_edit = QComboBox()

			self.load_time_type_edit.addItem(get_str('minutes'))
			self.load_time_type_edit.addItem(get_str('hours'))
			self.load_time_type_edit.addItem(get_str('days'))
			self.load_time_type_edit.addItem(get_str('months'))

			self.load_time_type_edit.setCurrentIndex(0)

			layout.addWidget(self.load_time_type_edit, 0, 2)

			upload_label_name = QLabel(f'<font size="4"> {get_str("upload_interval")} </font>')
			self.upload_time_edit = QSpinBox()
			layout.addWidget(upload_label_name, 1, 0)
			layout.addWidget(self.upload_time_edit, 1, 1)
			self.upload_time_type_edit = QComboBox()

			self.upload_time_type_edit.addItem(get_str('minutes'))
			self.upload_time_type_edit.addItem(get_str('hours'))
			self.upload_time_type_edit.addItem(get_str('days'))
			self.upload_time_type_edit.addItem(get_str('months'))

			self.upload_time_type_edit.setCurrentIndex(0)

			layout.addWidget(self.upload_time_type_edit, 1, 2)

			upload_time_label = QLabel(f'<font size="4"> {get_str("first_upload_time")} </font>')

			self.upload_hours_edit = QSpinBox()
			self.upload_hours_edit.setMinimum(0)
			self.upload_hours_edit.setMaximum(24)
			self.upload_hours_edit.setMaximumWidth(50)
			self.upload_minutes_edit = QSpinBox()
			self.upload_minutes_edit.setMinimum(0)
			self.upload_minutes_edit.setMaximum(60)
			self.upload_minutes_edit.setMaximumWidth(50)

			layout.addWidget(upload_time_label, 2, 0)
			layout.addWidget(self.upload_hours_edit, 2, 1)
			layout.addWidget(self.upload_minutes_edit, 2, 2)

		yes_button = QPushButton(get_str('yes'))
		yes_button.clicked.connect(self.on_yes)
		yes_button.setMaximumWidth(100)
		layout.addWidget(yes_button, 3, 0)

		no_button = QPushButton(get_str('no'))
		no_button.clicked.connect(self.on_no)
		no_button.setMaximumWidth(100)
		layout.addWidget(no_button, 3, 1)
		layout.setRowMinimumHeight(2, 75)

		if video_size is not None:
			video_size_pre_label = QLabel('video_size_label')
			video_size_pre_label.setText(get_str('media_size'))
			layout.addWidget(video_size_pre_label, 3, 0)

			video_size_label = QLabel('video_size_label')
			if video_size is int:
				video_size_label.setText(f'{video_size} MB')
			else:
				video_size_label.setText(f'{video_size}')
			layout.addWidget(video_size_label, 3, 1)

		self.state_service = StateService()
		self.need_interval = need_interval
		self.setLayout(layout)

	def on_no(self):
		self.upload_flag = False
		self.passed = True

		self.load_interval = int(self.load_time_edit.text())
		self.load_interval_type = self.load_time_type_edit.currentIndex()

		self.close()

	def on_yes(self):
		if self.need_interval:
			self.upload_interval = int(self.upload_time_edit.text())
			self.upload_interval_type = self.upload_time_type_edit.currentIndex()

			upload_hours = int(self.upload_hours_edit.text())
			upload_minutes = int(self.upload_minutes_edit.text())

			self.first_upload_date = datetime.now()
			if self.first_upload_date.hour > upload_hours:
				self.first_upload_date = self.first_upload_date + timedelta(days=1)

			self.first_upload_date = self.first_upload_date.replace(minute=upload_minutes, hour=upload_hours)

			self.load_interval = int(self.load_time_edit.text())
			self.load_interval_type = self.load_time_type_edit.currentIndex()

		# Выбираем аккаунты для выгрузки
		choose_accounts_for_uploading_form = ChooseAccountsForUploadingForm(self)
		choose_accounts_for_uploading_form.exec_()

		if choose_accounts_for_uploading_form.passed is False:
			return

		self.upload_targets = list()

		if len(choose_accounts_for_uploading_form.accounts) == 0:
			return

		for account in choose_accounts_for_uploading_form.accounts:
			self.upload_targets.append({
				'login': account.login,
				'hosting': account.hosting,
				'upload_target': account.url
			})

		self.upload_flag = True
		self.passed = True
		self.close()
