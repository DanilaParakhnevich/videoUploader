from PyQt5 import QtCore, QtWidgets
import load_page
import accounts

class Ui_BuharVideoUploader(object):
    def __init__(self):
        self.currentOption = None
        self.main_layout = None

    def setupUi(self, BuharVideoUploader):
        BuharVideoUploader.setObjectName("BuharVideoUploader")
        BuharVideoUploader.setWindowModality(QtCore.Qt.ApplicationModal)
        BuharVideoUploader.resize(954, 603)
        BuharVideoUploader.setStyleSheet("")
        BuharVideoUploader.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        BuharVideoUploader.setAnimated(True)
        BuharVideoUploader.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.central_widget = QtWidgets.QWidget(BuharVideoUploader)
        self.central_widget.setObjectName("centralwidget")

        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vertical_layout.setObjectName("verticalLayout")
        self.tab_widget = load_page.setupUi(self.central_widget) #Инициализация таблицы
        self.accounts_page = accounts.setupUi(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.accounts_page)
        self.accounts_page.hide()
        self.vertical_layout.addLayout(self.main_layout)

        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontalLayout")
        self.load_button = QtWidgets.QPushButton(self.central_widget)
        self.load_button.setObjectName("pushButton")
        self.horizontal_layout.addWidget(self.load_button)
        self.upload_button = QtWidgets.QPushButton(self.central_widget)
        self.upload_button.setObjectName("pushButton_3")
        self.horizontal_layout.addWidget(self.upload_button)
        self.accounts_button = QtWidgets.QPushButton(self.central_widget)
        self.accounts_button.setObjectName("pushButton_4")
        self.horizontal_layout.addWidget(self.accounts_button)
        self.settings_button = QtWidgets.QPushButton(self.central_widget)
        self.settings_button.setObjectName("pushButton_2")
        self.horizontal_layout.addWidget(self.settings_button)
        self.vertical_layout.addLayout(self.horizontal_layout)
        BuharVideoUploader.setCentralWidget(self.central_widget)

        self.retranslateUi(BuharVideoUploader)
        QtCore.QMetaObject.connectSlotsByName(BuharVideoUploader)

    def retranslateUi(self, BuharVideoUploader):
        _translate = QtCore.QCoreApplication.translate
        BuharVideoUploader.setWindowTitle(_translate("BuharVideoUploader", "BuharVideoUploader"))
        self.load_button.setText(_translate("BuharVideoUploader", "Выгрузить"))
        self.upload_button.setText(_translate("BuharVideoUploader", "Загрузить"))
        self.accounts_button.setText(_translate("BuharVideoUploader", "Аккаунты"))
        self.settings_button.setText(_translate("BuharVideoUploader", "Настройки"))

        self.load_button.clicked.connect(self.b1)
        self.accounts_button.clicked.connect(self.b2)
    ##сигналы и слоты + добавление табов + отрисовка остальных страниц и сохранение предыдущих

    a = False
    def b1(self):
        self.accounts_page.hide()
        self.tab_widget.show()

    def b2(self):
        self.accounts_page.show()
        self.tab_widget.hide()




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BuharVideoUploader = QtWidgets.QMainWindow()
    ui = Ui_BuharVideoUploader()
    ui.setupUi(BuharVideoUploader)
    BuharVideoUploader.show()
    sys.exit(app.exec_())
