from PyQt5 import QtCore, QtWidgets
from gui.ChannelsPage import ChannelsPageWidget
from gui.AccountsPage import AccountsPageWidget
from gui.DownloadQueuePage import DownloadQueuePageWidget
from gui.UploadQueuePage import UploadQueuePageWidget
from gui.LoadPage import LoadPageWidget
from gui.SettingsPage import SettingsPage
from service.LocalizationService import *


# Этот класс хранит в себе все страницы с логикой
class Ui_BuxarVideoUploader(object):
    def __init__(self):
        self.currentOption = None
        self.main_layout = None

    def setupUi(self, ui, version):
        ui.setObjectName(f'BuxarVideoUploader {version}')
        ui.setWindowModality(QtCore.Qt.ApplicationModal)
        ui.resize(950, 600)
        ui.setMaximumSize(950, 600)
        ui.setMinimumSize(949, 599)
        ui.setStyleSheet("")
        ui.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        ui.setAnimated(True)
        ui.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.central_widget = QtWidgets.QWidget(ui)
        self.central_widget.setObjectName("centralwidget")

        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vertical_layout.setObjectName("verticalLayout")
        self.load_page = LoadPageWidget(self.central_widget)
        self.channels_page = ChannelsPageWidget(self.central_widget)
        self.accounts_page = AccountsPageWidget(self.central_widget)
        self.download_queue_page = DownloadQueuePageWidget(self.central_widget)
        self.upload_queue_page = UploadQueuePageWidget(self.central_widget)
        self.settings_dialog = SettingsPage(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.load_page)
        self.main_layout.addWidget(self.accounts_page)
        self.main_layout.addWidget(self.channels_page)
        self.main_layout.addWidget(self.download_queue_page)
        self.main_layout.addWidget(self.upload_queue_page)
        self.accounts_page.hide()
        self.channels_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()
        self.vertical_layout.addLayout(self.main_layout)

        self.horizontal_action_layout = QtWidgets.QHBoxLayout()
        self.horizontal_action_layout.setObjectName('horizontal_action_layout')
        self.horizontal_action_layout.setAlignment(QtCore.Qt.AlignBottom)

        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontalLayout")
        self.load_button = QtWidgets.QPushButton(self.central_widget)
        self.load_button.setObjectName("pushButton")
        self.horizontal_layout.addWidget(self.load_button)
        self.channels_button = QtWidgets.QPushButton(self.central_widget)
        self.channels_button.setObjectName("channels_button")
        self.horizontal_layout.addWidget(self.channels_button)
        self.accounts_button = QtWidgets.QPushButton(self.central_widget)
        self.accounts_button.setObjectName("accounts_button")
        self.horizontal_layout.addWidget(self.accounts_button)
        self.download_queue_page_button = QtWidgets.QPushButton(self.central_widget)
        self.download_queue_page_button.setObjectName("download_queue_page_button")
        self.horizontal_layout.addWidget(self.download_queue_page_button)
        self.upload_queue_page_button = QtWidgets.QPushButton(self.central_widget)
        self.upload_queue_page_button.setObjectName("upload_queue_page_button")
        self.horizontal_layout.addWidget(self.upload_queue_page_button)
        self.settings_button = QtWidgets.QPushButton(self.central_widget)
        self.settings_button.setObjectName("settings_button")
        self.horizontal_layout.addWidget(self.settings_button)
        self.vertical_layout.addLayout(self.horizontal_action_layout)
        self.vertical_layout.addLayout(self.horizontal_layout)
        ui.setCentralWidget(self.central_widget)

        self.retranslate_ui(ui, version)
        QtCore.QMetaObject.connectSlotsByName(ui)

    def retranslate_ui(self, BuxarVideoUploader, version):
        BuxarVideoUploader.setWindowTitle(f'BuxarVideoUploader: {version}')
        self.load_button.setText(get_str('download_page'))
        self.channels_button.setText(get_str('channels_page'))
        self.accounts_button.setText(get_str('accounts_page'))
        self.download_queue_page_button.setText(get_str('download_queue_page'))
        self.upload_queue_page_button.setText(get_str('upload_queue_page'))
        self.settings_button.setText(get_str('settings_page'))

        self.load_button.clicked.connect(self.show_load_page)
        self.load_button.setStyleSheet("border: 2px solid blue; border-radius: 5px")

        self.channels_button.clicked.connect(self.show_channels_page)
        self.accounts_button.clicked.connect(self.show_accounts_page)
        self.download_queue_page_button.clicked.connect(self.show_download_queue_page)
        self.upload_queue_page_button.clicked.connect(self.show_upload_queue_page)
        self.settings_button.clicked.connect(self.show_settings_dialog)

    def show_settings_dialog(self):
        self.settings_dialog.exec_()

    def show_load_page(self):
        self.load_button.setStyleSheet("border: 2px solid blue; border-radius: 5px")

        self.channels_button.setStyleSheet("")
        self.accounts_button.setStyleSheet("")
        self.download_queue_page_button.setStyleSheet("")
        self.upload_queue_page_button.setStyleSheet("")

        for i in reversed(range(self.horizontal_action_layout.count())):
            self.horizontal_action_layout.itemAt(i).widget().setParent(None)

        self.channels_page.hide()
        self.load_page.show()
        self.accounts_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()

    def show_channels_page(self):
        self.channels_button.setStyleSheet("border: 2px solid blue; border-radius: 5px")

        self.load_button.setStyleSheet("")
        self.accounts_button.setStyleSheet("")
        self.download_queue_page_button.setStyleSheet("")
        self.upload_queue_page_button.setStyleSheet("")

        for i in reversed(range(self.horizontal_action_layout.count())):
            self.horizontal_action_layout.itemAt(i).widget().setParent(None)

        self.horizontal_action_layout.addWidget(self.channels_page.comboBox)
        self.horizontal_action_layout.addWidget(self.channels_page.url_edit)
        self.horizontal_action_layout.addWidget(self.channels_page.add_button)

        self.channels_page.show()
        self.load_page.hide()
        self.accounts_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()

    def show_accounts_page(self):
        self.accounts_button.setStyleSheet("border: 2px solid blue; border-radius: 5px")

        self.channels_button.setStyleSheet("")
        self.load_button.setStyleSheet("")
        self.download_queue_page_button.setStyleSheet("")
        self.upload_queue_page_button.setStyleSheet("")

        for i in reversed(range(self.horizontal_action_layout.count())):
            self.horizontal_action_layout.itemAt(i).widget().setParent(None)

        self.horizontal_action_layout.addWidget(self.accounts_page.comboBox)
        self.horizontal_action_layout.addWidget(self.accounts_page.add_button)

        self.channels_page.hide()
        self.load_page.hide()
        self.accounts_page.show()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()

    def show_download_queue_page(self):
        self.download_queue_page_button.setStyleSheet("border: 2px solid blue; border-radius: 5px")

        self.channels_button.setStyleSheet("")
        self.load_button.setStyleSheet("")
        self.accounts_button.setStyleSheet("")
        self.upload_queue_page_button.setStyleSheet("")

        for i in reversed(range(self.horizontal_action_layout.count())):
            self.horizontal_action_layout.itemAt(i).widget().setParent(None)

        self.horizontal_action_layout.addWidget(self.download_queue_page.add_button)

        self.channels_page.hide()
        self.load_page.hide()
        self.accounts_page.hide()
        self.download_queue_page.show()
        self.upload_queue_page.hide()

    def show_upload_queue_page(self):
        self.upload_queue_page_button.setStyleSheet("border: 2px solid blue; border-radius: 5px")

        self.channels_button.setStyleSheet("")
        self.load_button.setStyleSheet("")
        self.accounts_button.setStyleSheet("")
        self.download_queue_page_button.setStyleSheet("")

        for i in reversed(range(self.horizontal_action_layout.count())):
            self.horizontal_action_layout.itemAt(i).widget().setParent(None)

        self.horizontal_action_layout.addWidget(self.upload_queue_page.add_button)

        self.channels_page.hide()
        self.load_page.hide()
        self.accounts_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.show()
