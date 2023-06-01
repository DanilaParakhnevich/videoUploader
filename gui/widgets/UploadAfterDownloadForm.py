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
	passed = False

	def __init__(self, parent, need_interval: bool = True):
		super().__init__(parent)
		self.setWindowTitle(get_str('upload_video_after_download'))
		self.resize(300, 120)

		layout = QGridLayout()
		if need_interval:
			self.resize(500, 120)
			label_name = QLabel(f'<font size="4"> {get_str("interval")} </font>')
			self.time_edit = QSpinBox()
			layout.addWidget(label_name, 0, 0)
			layout.addWidget(self.time_edit, 0, 1)
			self.time_type_edit = QComboBox()

			self.time_type_edit.addItem(get_str('minutes'))
			self.time_type_edit.addItem(get_str('hours'))
			self.time_type_edit.addItem(get_str('days'))
			self.time_type_edit.addItem(get_str('months'))

			self.time_type_edit.setCurrentIndex(0)

			layout.addWidget(self.time_type_edit, 0, 2)

		yes_button = QPushButton(get_str('yes'))
		yes_button.clicked.connect(self.on_yes)
		yes_button.setMaximumWidth(100)
		layout.addWidget(yes_button, 2, 0)

		no_button = QPushButton(get_str('no'))
		no_button.clicked.connect(self.on_no)
		no_button.setMaximumWidth(100)
		layout.addWidget(no_button, 2, 1)
		layout.setRowMinimumHeight(2, 75)

		self.state_service = StateService()
		self.need_interval = need_interval
		self.setLayout(layout)

	def on_no(self):
		self.upload_flag = False
		self.passed = True
		self.close()

	def on_yes(self):
		if self.need_interval:
			self.upload_interval = int(self.time_edit.text())
			self.upload_interval_type = self.time_type_edit.currentIndex()

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
