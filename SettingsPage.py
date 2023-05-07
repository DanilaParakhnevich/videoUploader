from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator
from model.Settings import Settings
from service.StateService import StateService


class SettingsPage(QtWidgets.QDialog):
    state_service = StateService()

    def __init__(self, central_widget):
        super(SettingsPage, self).__init__(central_widget)
        self.old_settings = self.state_service.get_settings()
        self.settings_box = QtWidgets.QWidget()
        self.scroll = QtWidgets.QScrollArea(self)
        self.resize(443, 352)

        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.settings_box)
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumSize(self.width(), self.height())
        self.setObjectName("Settings")

        self.gridLayout = QtWidgets.QGridLayout(self.settings_box)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.main_settings = QtWidgets.QLabel(self)
        self.main_settings.setObjectName("main_settings")
        self.main_settings.setMinimumWidth(200)
        self.gridLayout.addWidget(self.settings_box, 0, 0)

        self.language_label = QtWidgets.QLabel("Язык")
        self.language_box = QtWidgets.QComboBox()
        self.language_box.setCurrentText(self.old_settings.language)
        self.gridLayout.addWidget(self.language_label, 1, 0)
        self.gridLayout.addWidget(self.language_box, 1, 1)

        self.download_strategy_label = QtWidgets.QLabel()
        self.download_strategy_box = QtWidgets.QComboBox()
        self.download_strategy_box.addItem('Вручную', 0)
        self.download_strategy_box.addItem('Последовательная', 1)
        self.download_strategy_box.addItem('Параллельная', 2)
        self.download_strategy_box.setCurrentIndex(self.old_settings.download_strategy)
        self.download_strategy_box.currentIndexChanged.connect(self.on_strategy_changed)
        self.gridLayout.addWidget(self.download_strategy_label, 2, 0)
        self.gridLayout.addWidget(self.download_strategy_box, 2, 1)

        self.pack_count_label = QtWidgets.QLabel("Количество пакетов")
        self.pack_count_edit = QtWidgets.QLineEdit()
        self.pack_count_edit.setMaximumWidth(150)
        self.pack_count_edit.setText(str(self.old_settings.pack_count))
        self.gridLayout.addWidget(self.pack_count_label, 3, 0)
        self.gridLayout.addWidget(self.pack_count_edit, 3, 1)

        if self.download_strategy_box.currentData() == 0:
            self.pack_count_label.hide()
            self.pack_count_edit.hide()

        self.choose_dir_button = QtWidgets.QPushButton(self.settings_box)
        self.choose_dir_button.setObjectName("choose_dir_button")
        self.choose_dir_button.setMaximumWidth(50)
        self.gridLayout.addWidget(self.choose_dir_button, 5, 1)
        self.choose_dir_label = QtWidgets.QLabel(self.settings_box)
        self.choose_dir_label.setObjectName("choose_dir_label")
        self.gridLayout.addWidget(self.choose_dir_label, 5, 0)

        self.save_button = QtWidgets.QPushButton(self.settings_box)
        self.save_button.setObjectName("save_button")
        self.save_button.setMaximumWidth(80)
        self.save_button.clicked.connect(self.on_save)
        self.gridLayout.addWidget(self.save_button, 6, 0)

        self.autostart = QtWidgets.QCheckBox(self.settings_box)
        self.autostart.setObjectName("autostart")
        self.autostart.setChecked(self.old_settings.autostart)
        self.gridLayout.addWidget(self.autostart, 6, 1)

        # self.save_label = QtWidgets.QLabel(self.settings_box)
        # self.save_label.setObjectName("save_label")
        # self.gridLayout.addWidget(self.save_label, 6, 1)
        self.retranslate_ui()

    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Settings", "Настройки"))
        self.main_settings.setText(_translate("Settings", "Системные настройки:"))
        self.language_label.setText(_translate("Settings", "Язык"))
        self.download_strategy_label.setText(_translate("Settings", "Стратегия загрузки"))
        self.pack_count_label.setText(_translate("Settings", "Количество медиа для одновременной загрузки"))
        self.autostart.setText(_translate("Settings", "Автозапуск приложения"))
        self.choose_dir_label.setText(_translate("Settings", "Выбор пути загрузки"))
        self.save_button.setText(_translate("Settings", "Сохранить"))
        # self.save_label.setText(_translate("Settings", "Сохранить"))

    def on_strategy_changed(self, index):
        if index == 0:
            self.pack_count_label.hide()
            self.pack_count_edit.hide()
        else:
            self.pack_count_label.show()
            self.pack_count_edit.show()

    def on_save(self):

        if self.old_settings.download_strategy != self.download_strategy_box.currentIndex():
            msg = QtWidgets.QMessageBox()
            msg.setText('Для применения настроек стратегии загрузки требуется перезапуск приложения')
            msg.exec_()

        self.state_service.save_settings(
            Settings(
                language=self.language_box.currentData(),
                download_strategy=self.download_strategy_box.currentData(),
                autostart=self.autostart.isChecked(),
                download_dir='',
                pack_count=int(self.pack_count_edit.text())))
