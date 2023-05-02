from PyQt5 import QtCore, QtWidgets


class SettingsPage(QtWidgets.QDialog):

    def __init__(self, central_widget):

        super(SettingsPage, self).__init__(central_widget)

        self.setObjectName("Settings")
        self.resize(443, 352)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_settings = QtWidgets.QLabel(self)
        self.main_settings.setObjectName("main_settings")
        self.main_settings.setMinimumWidth(200)
        self.verticalLayout.addWidget(self)
        self.language_layout = QtWidgets.QHBoxLayout()
        self.language_layout.setObjectName("language_layout")
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setObjectName("language")
        self.language_layout.addWidget(self.comboBox)
        self.language_label = QtWidgets.QLabel(self)
        self.language_label.setObjectName("language_label")
        self.language_layout.addWidget(self.language_label)
        self.verticalLayout.addLayout(self.language_layout)
        self.autostart = QtWidgets.QCheckBox(self)
        self.autostart.setObjectName("autostart")
        self.verticalLayout.addWidget(self.autostart)
        self.choose_dir_layout = QtWidgets.QHBoxLayout()
        self.choose_dir_layout.setObjectName("choose_dir_layout")
        self.choose_dir_button = QtWidgets.QPushButton(self)
        self.choose_dir_button.setObjectName("choose_dir_button")
        self.choose_dir_button.setMaximumWidth(50)
        self.choose_dir_layout.addWidget(self.choose_dir_button)
        self.choose_dir_label = QtWidgets.QLabel(self)
        self.choose_dir_label.setObjectName("choose_dir_label")
        self.choose_dir_layout.addWidget(self.choose_dir_label)
        self.verticalLayout.addLayout(self.choose_dir_layout)
        self.save_layout = QtWidgets.QHBoxLayout()
        self.save_layout.setObjectName("save_layout")
        self.save_button = QtWidgets.QPushButton(self)
        self.save_button.setObjectName("save_button")
        self.save_button.setMaximumWidth(50)
        self.save_layout.addWidget(self.save_button)
        self.save_label = QtWidgets.QLabel(self)
        self.save_label.setObjectName("save_label")
        self.save_layout.addWidget(self.save_label)
        self.verticalLayout.addLayout(self.save_layout)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Settings", "Настройки"))
        self.main_settings.setText(_translate("Settings", "Системные настройки:"))
        self.language_label.setText(_translate("Settings", "Язык"))
        self.autostart.setText(_translate("Settings", "Автозапуск приложения"))
        self.choose_dir_label.setText(_translate("Settings", "Выбор пути загрузки"))
        self.save_label.setText(_translate("Settings", "Сохранить"))
