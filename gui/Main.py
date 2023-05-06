from PyQt5 import QtCore, QtWidgets
from gui.Channels import ChannelsPageWidget
from gui.Accounts import AccountsPageWidget
from gui.DownloadQueuePage import DownloadQueuePageWidget
from gui.UploadQueuePage import UploadQueuePageWidget
from gui.SettingsPage import SettingsPage
import LoadPage


class Ui_BuharVideoUploader(object):
    def __init__(self):
        self.currentOption = None
        self.main_layout = None

    def setupUi(self, ui):
        ui.setObjectName("BuharVideoUploader")
        ui.setWindowModality(QtCore.Qt.ApplicationModal)
        ui.resize(954, 603)
        ui.setStyleSheet("")
        ui.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        ui.setAnimated(True)
        ui.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.central_widget = QtWidgets.QWidget(ui)
        self.central_widget.setObjectName("centralwidget")

        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vertical_layout.setObjectName("verticalLayout")
        self.main_page = LoadPage.LoadPageWidget(self.central_widget)
        self.channels_page = ChannelsPageWidget(self.central_widget)
        self.accounts_page = AccountsPageWidget(self.central_widget)
        self.download_queue_page = DownloadQueuePageWidget(self.central_widget)
        self.upload_queue_page = UploadQueuePageWidget(self.central_widget)
        self.settings_dialog = SettingsPage(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.main_page)
        self.main_layout.addWidget(self.accounts_page)
        self.main_layout.addWidget(self.channels_page)
        self.main_layout.addWidget(self.download_queue_page)
        self.main_layout.addWidget(self.upload_queue_page)
        self.accounts_page.hide()
        self.channels_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()
        self.vertical_layout.addLayout(self.main_layout)

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
        self.vertical_layout.addLayout(self.horizontal_layout)
        ui.setCentralWidget(self.central_widget)

        self.retranslate_ui(ui)
        QtCore.QMetaObject.connectSlotsByName(ui)

    def retranslate_ui(self, BuharVideoUploader):
        _translate = QtCore.QCoreApplication.translate
        BuharVideoUploader.setWindowTitle(_translate("BuharVideoUploader", "BuharVideoUploader"))
        self.load_button.setText(_translate("BuharVideoUploader", "Выгрузить"))
        self.channels_button.setText(_translate("BuharVideoUploader", "Каналы"))
        self.accounts_button.setText(_translate("BuharVideoUploader", "Аккаунты"))
        self.download_queue_page_button.setText(_translate("BuharVideoUploader", "Очередь загрузки"))
        self.upload_queue_page_button.setText(_translate("BuharVideoUploader", "Очередь выгрузки"))
        self.settings_button.setText(_translate("BuharVideoUploader", "Настройки"))

        self.load_button.clicked.connect(self.show_main_page)
        self.channels_button.clicked.connect(self.show_channels_page)
        self.accounts_button.clicked.connect(self.show_accounts_page)
        self.download_queue_page_button.clicked.connect(self.show_download_queue_page)
        self.upload_queue_page_button.clicked.connect(self.show_upload_queue_page)
        self.settings_button.clicked.connect(self.show_settings_dialog)

    def show_settings_dialog(self):
        self.settings_dialog.exec_()

    def show_main_page(self):
        self.channels_page.hide()
        self.main_page.show()
        self.accounts_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()

    def show_channels_page(self):
        self.channels_page.show()
        self.main_page.hide()
        self.accounts_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()

    def show_accounts_page(self):
        self.channels_page.hide()
        self.main_page.hide()
        self.accounts_page.show()
        self.download_queue_page.hide()
        self.upload_queue_page.hide()

    def show_download_queue_page(self):
        self.channels_page.hide()
        self.main_page.hide()
        self.accounts_page.hide()
        self.download_queue_page.show()
        self.upload_queue_page.hide()

    def show_upload_queue_page(self):
        self.channels_page.hide()
        self.main_page.hide()
        self.accounts_page.hide()
        self.download_queue_page.hide()
        self.upload_queue_page.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BuharVideoUploader = QtWidgets.QMainWindow()
    ui = Ui_BuharVideoUploader()
    ui.setupUi(BuharVideoUploader)
    BuharVideoUploader.show()
    sys.exit(app.exec_())
