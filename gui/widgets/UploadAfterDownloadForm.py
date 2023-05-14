from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QSpinBox, QGridLayout, QComboBox, QMessageBox)

from gui.widgets.ChooseAccountForm import ChooseAccountForm
from gui.widgets.ChooseChannelForm import ChooseChannelForm
from gui.widgets.ChooseHostingForm import ChooseHostingForm
from service.LocalizationService import *


class UploadAfterDownloadForm(QDialog):

	upload_flag = False
	upload_interval = None
	upload_interval_type = None
	upload_account = None
	upload_target = None
	upload_hosting = None
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

		# В случае если выгрузка необходима, нужно выбрать хостинг для выгрузки и соответственно аккаунт
		choose_hosting_form = ChooseHostingForm(self)
		choose_hosting_form.exec_()

		if choose_hosting_form.hosting is None or choose_hosting_form.passed is False:
			self.close()
			return

		self.upload_hosting = choose_hosting_form.hosting
		accounts = self.state_service.get_accounts_by_hosting(choose_hosting_form.hosting.name)

		if len(accounts) == 0:
			msg = QMessageBox()
			msg.setText(f'{get_str("not_found_accounts_for_videohosting")}: {choose_hosting_form.hosting.name}')
			msg.exec_()
			self.close()
			return

		choose_account_form = ChooseAccountForm(self, accounts)
		choose_account_form.exec_()

		if choose_account_form.account is None:
			self.close()
			return

		self.upload_account = choose_account_form.account

		if choose_hosting_form.hosting.value[0].need_to_be_uploaded_to_special_source():
			# В некоторых ситуациях, допустим с Telegram, для выгрузки необходимо указать дополнительную информацию
			# такую, как то, на какой именно канал по аккаунту нужно выгружать видео

			channels = self.state_service.get_channel_by_hosting(choose_hosting_form.hosting.name)

			if len(channels) == 0:
				msg = QMessageBox()
				msg.setText(f'{get_str("not_found_channels_for_videohosting")}: {choose_hosting_form.hosting.name}')
				msg.exec_()
				self.close()
				return

			form = ChooseChannelForm(self, channels)
			form.exec_()

			if form.passed:
				self.upload_target = form.channel.url
			else:
				self.close()
				return

		self.upload_flag = True
		self.passed = True
		self.close()
