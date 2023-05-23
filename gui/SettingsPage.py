from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator

from gui.widgets.EventsListForm import EventsListForm
from model.Settings import Settings
from service.LocalizationService import *


class SettingsPage(QtWidgets.QDialog):
    state_service = StateService()

    def __init__(self, central_widget):

        super(SettingsPage, self).__init__(central_widget)
        self.old_settings = self.state_service.get_settings()
        self.settings_box = QtWidgets.QWidget()
        self.scroll = QtWidgets.QScrollArea(self)
        self.resize(700, 480)

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

        self.language_label = QtWidgets.QLabel(get_str('language'))
        self.language_box = QtWidgets.QComboBox()
        for language in get_all_locales():
            self.language_box.addItem(language, language)

        self.language_box.setCurrentText(self.old_settings.language)

        self.gridLayout.addWidget(self.language_label, 1, 0)
        self.gridLayout.addWidget(self.language_box, 1, 1)

        self.download_strategy_label = QtWidgets.QLabel()
        self.download_strategy_box = QtWidgets.QComboBox()
        self.download_strategy_box.addItem(get_str('manually_item'), 0)
        self.download_strategy_box.addItem(get_str('serial_item'), 1)
        self.download_strategy_box.addItem(get_str('parallel_item'), 2)
        self.download_strategy_box.setCurrentIndex(self.old_settings.download_strategy)
        self.download_strategy_box.currentIndexChanged.connect(self.on_strategy_changed)
        self.gridLayout.addWidget(self.download_strategy_label, 2, 0)
        self.gridLayout.addWidget(self.download_strategy_box, 2, 1)

        self.pack_count_label = QtWidgets.QLabel(get_str('pack_count'))
        self.pack_count_edit = QtWidgets.QLineEdit()
        self.pack_count_edit.setValidator(QIntValidator(1, 9))
        self.pack_count_edit.setMaximumWidth(150)
        self.pack_count_edit.setText(str(self.old_settings.pack_count))
        self.gridLayout.addWidget(self.pack_count_label, 3, 0)
        self.gridLayout.addWidget(self.pack_count_edit, 3, 1)

        if self.download_strategy_box.currentData() != 2:
            self.pack_count_label.hide()
            self.pack_count_edit.hide()

        self.choose_dir_button = QtWidgets.QPushButton(self.settings_box)
        self.choose_dir_button.setObjectName("choose_dir_button")
        self.choose_dir_button.setMaximumWidth(200)
        self.choose_dir_button.clicked.connect(self.pick_new)
        self.gridLayout.addWidget(self.choose_dir_button, 4, 1)
        self.choose_dir_label = QtWidgets.QLabel(self.settings_box)
        self.choose_dir_label.setObjectName("choose_dir_label")
        self.gridLayout.addWidget(self.choose_dir_label, 4, 0)

        self.add_localization_button = QtWidgets.QPushButton(self.settings_box)
        self.add_localization_button.setObjectName("add_localization_button")
        self.add_localization_button.setMaximumWidth(200)
        self.add_localization_button.clicked.connect(self.add_locale)
        self.gridLayout.addWidget(self.add_localization_button, 5, 1)
        self.add_localization_label = QtWidgets.QLabel(self.settings_box)
        self.add_localization_label.setObjectName("add_localization_label")
        self.gridLayout.addWidget(self.add_localization_label, 5, 0)

        self.rate_limit_label = QtWidgets.QLabel(get_str('download_video_speed_limit'))
        self.rate_limit_edit = QtWidgets.QLineEdit()
        self.rate_limit_edit.setValidator(QIntValidator(0, 99999))
        self.rate_limit_edit.setMaximumWidth(150)
        self.rate_limit_edit.setText(str(self.old_settings.rate_limit))
        self.gridLayout.addWidget(self.rate_limit_label, 6, 0)
        self.gridLayout.addWidget(self.rate_limit_edit, 6, 1)

        self.events_page_button = QtWidgets.QPushButton(self.settings_box)
        self.events_page_button.setObjectName("events_page_button")
        self.events_page_button.setMaximumWidth(200)
        self.events_page_button.clicked.connect(self.open_events_page)
        self.gridLayout.addWidget(self.events_page_button, 7, 1)
        self.events_label = QtWidgets.QLabel(self.settings_box)
        self.events_label.setObjectName("add_localization_label")
        self.gridLayout.addWidget(self.events_label, 7, 0)

        self.send_crash_notifications = QtWidgets.QCheckBox(self.settings_box)
        self.send_crash_notifications.setObjectName("autostart")
        self.send_crash_notifications.setChecked(self.old_settings.send_crash_notifications)
        self.gridLayout.addWidget(self.send_crash_notifications, 8, 0)

        self.save_button = QtWidgets.QPushButton(self.settings_box)
        self.save_button.setObjectName("save_button")
        self.save_button.setMaximumWidth(80)
        self.save_button.clicked.connect(self.on_save)
        self.gridLayout.addWidget(self.save_button, 9, 0)

        self.autostart_button = QtWidgets.QPushButton(self.settings_box)
        self.autostart_button.clicked.connect(self.add_autostart)
        self.autostart_button.setObjectName("autostart")
        self.gridLayout.addWidget(self.autostart_button, 9, 1)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(get_str('settings_page'))
        self.main_settings.setText(f'{get_str("system_settings")}:')
        self.language_label.setText(get_str('language'))
        self.download_strategy_label.setText(get_str('download_strategy'))
        self.pack_count_label.setText(get_str('count_media_for_synchronous_downloading'))
        self.rate_limit_label.setText(get_str('download_speed_limit'))
        self.autostart_button.setText(get_str('application_autostart'))
        self.events_label.setText(get_str('events'))
        self.choose_dir_label.setText(get_str('choose_the_download_path'))
        self.send_crash_notifications.setText(get_str('send_crash_notifications'))
        self.add_localization_label.setText(get_str('add_localization'))
        self.choose_dir_button.setText(self.old_settings.download_dir)
        self.save_button.setText(get_str('save'))

    def pick_new(self):
        dialog = QtWidgets.QFileDialog()
        folder_path = dialog.getExistingDirectory(None, get_str('choose_dir'))
        if folder_path != '':
            self.choose_dir_button.setText(folder_path)

    def add_locale(self):
        dialog = QtWidgets.QFileDialog()
        folder_path = dialog.getOpenFileName(None, get_str('choose_loc_file'), "", "JSON (*.json)")

        if folder_path[0] is not '':
            try:
                add_new_locale(folder_path[0])

                self.language_box.clear()

                for language in get_all_locales():
                    self.language_box.addItem(language, language)
            except:
                msg = QtWidgets.QMessageBox()
                msg.setText(get_str('bad_locale_file'))
                msg.exec_()

    def open_events_page(self):
        events = EventsListForm(self)
        events.exec_()

    def add_autostart(self):
        return

    def on_strategy_changed(self, index):
        if index != 2:
            self.pack_count_label.hide()
            self.pack_count_edit.hide()
        else:
            self.pack_count_label.show()
            self.pack_count_edit.show()

    def on_save(self):

        if self.old_settings.download_strategy != self.download_strategy_box.currentIndex() \
                or self.old_settings.pack_count != int(self.pack_count_edit.text()):
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('for_applying_strategy_settings_need_to_restart'))
            msg.exec_()

        if self.old_settings.language != self.language_box.currentData():
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('for_applying_localization_settings_need_to_restart'))
            msg.exec_()

        self.state_service.save_settings(
            Settings(
                language=self.language_box.currentData(),
                download_strategy=self.download_strategy_box.currentData(),
                download_dir=self.choose_dir_button.text(),
                pack_count=int(self.pack_count_edit.text()),
                rate_limit=int(self.rate_limit_edit.text()),
                send_crash_notifications=self.send_crash_notifications.checkState() != 0))
