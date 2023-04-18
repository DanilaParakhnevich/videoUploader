from PyQt5 import QtCore, QtWidgets
from gui.Channels import ChannelsPageWidget
from gui.Accounts import AccountsPageWidget
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
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.main_page)
        self.main_layout.addWidget(self.accounts_page)
        self.main_layout.addWidget(self.channels_page)
        self.accounts_page.hide()
        self.channels_page.hide()
        self.vertical_layout.addLayout(self.main_layout)

        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontalLayout")
        self.load_button = QtWidgets.QPushButton(self.central_widget)
        self.load_button.setObjectName("pushButton")
        self.horizontal_layout.addWidget(self.load_button)
        # self.upload_button = QtWidgets.QPushButton(self.central_widget)
        # self.upload_button.setObjectName("pushButton_3")
        # self.horizontal_layout.addWidget(self.upload_button)
        self.channels_button = QtWidgets.QPushButton(self.central_widget)
        self.channels_button.setObjectName("pushButton_4")
        self.horizontal_layout.addWidget(self.channels_button)
        self.accounts_button = QtWidgets.QPushButton(self.central_widget)
        self.accounts_button.setObjectName("pushButton_4")
        self.horizontal_layout.addWidget(self.accounts_button)
        self.settings_button = QtWidgets.QPushButton(self.central_widget)
        self.settings_button.setObjectName("pushButton_2")
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
        self.settings_button.setText(_translate("BuharVideoUploader", "Настройки"))

        self.load_button.clicked.connect(self.show_main_page)
        self.channels_button.clicked.connect(self.show_channels_page)
        self.accounts_button.clicked.connect(self.show_accounts_page)

    def show_main_page(self):
        self.channels_page.hide()
        self.main_page.show()
        self.accounts_page.hide()

    def show_channels_page(self):
        self.channels_page.show()
        self.main_page.hide()
        self.accounts_page.hide()

    def show_accounts_page(self):
        self.channels_page.hide()
        self.main_page.hide()
        self.accounts_page.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BuharVideoUploader = QtWidgets.QMainWindow()
    ui = Ui_BuharVideoUploader()
    ui.setupUi(BuharVideoUploader)
    BuharVideoUploader.show()
    sys.exit(app.exec_())
