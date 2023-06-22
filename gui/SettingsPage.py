import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator

from gui.widgets.ChooseVideoQualityComboBox import ChooseVideoQualityComboBox
from gui.widgets.EventsListForm import EventsListForm
from gui.widgets.ExstensionChooserComboBox import ExtensionChooserComboBox
from gui.widgets.FormatChooserComboBox import FormatChooserComboBox
from model.Settings import Settings
from service.LocalizationService import *
from service.LoggingService import log_error
from service.VersionService import VersionService


class SettingsPage(QtWidgets.QDialog):
    state_service = StateService()

    def __init__(self, central_widget):

        super(SettingsPage, self).__init__(central_widget)
        self.old_settings = self.state_service.get_settings()
        self.settings_box = QtWidgets.QWidget()
        self.scroll = QtWidgets.QScrollArea(self)
        self.setFixedSize(900, 800)

        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.settings_box)
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumSize(self.width(), self.height())
        self.setObjectName("Settings")

        self.gridLayout = QtWidgets.QGridLayout(self.settings_box)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(-100)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.main_settings = QtWidgets.QLabel()
        self.main_settings.setObjectName("main_settings")
        self.main_settings.setMinimumWidth(200)
        self.main_settings.setMaximumHeight(20)
        self.gridLayout.addWidget(self.main_settings, 1, 0)
        self.gridLayout.addWidget(self.settings_box, 0, 0)

        self.version_label = QtWidgets.QLabel()
        self.version_label.setText(VersionService().get_current_client_version())
        self.version_label.setMaximumHeight(20)
        self.gridLayout.addWidget(self.version_label, 1, 1)

        self.language_label = QtWidgets.QLabel(get_str('language'))
        self.language_box = QtWidgets.QComboBox()
        for language in get_all_locales():
            self.language_box.addItem(language, language)

        self.language_box.setCurrentText(self.old_settings.language)

        self.gridLayout.addWidget(self.language_label, 2, 0)
        self.gridLayout.addWidget(self.language_box, 2, 1)

        self.download_strategy_label = QtWidgets.QLabel()
        self.download_strategy_box = QtWidgets.QComboBox()
        self.download_strategy_box.addItem(get_str('manually_item'), 0)
        self.download_strategy_box.addItem(get_str('serial_item'), 1)
        self.download_strategy_box.addItem(get_str('parallel_item'), 2)
        self.download_strategy_box.setCurrentIndex(self.old_settings.download_strategy)
        self.download_strategy_box.currentIndexChanged.connect(self.on_strategy_changed)
        self.gridLayout.addWidget(self.download_strategy_label, 3, 0)
        self.gridLayout.addWidget(self.download_strategy_box, 3, 1)

        self.pack_count_label = QtWidgets.QLabel(get_str('pack_count'))
        self.pack_count_edit = QtWidgets.QLineEdit()
        self.pack_count_edit.setValidator(QIntValidator(1, 9))
        self.pack_count_edit.setMaximumWidth(150)
        self.pack_count_edit.setText(str(self.old_settings.pack_count))
        self.gridLayout.addWidget(self.pack_count_label, 4, 0)
        self.gridLayout.addWidget(self.pack_count_edit, 4, 1)

        if self.download_strategy_box.currentData() != 2:
            self.pack_count_label.hide()
            self.pack_count_edit.hide()

        self.choose_dir_button = QtWidgets.QPushButton(self.settings_box)
        self.choose_dir_button.setObjectName("choose_dir_button")
        self.choose_dir_button.setMaximumWidth(200)
        self.choose_dir_button.clicked.connect(self.pick_new)
        self.gridLayout.addWidget(self.choose_dir_button, 5, 1)
        self.choose_dir_label = QtWidgets.QLabel(self.settings_box)
        self.choose_dir_label.setObjectName("choose_dir_label")
        self.gridLayout.addWidget(self.choose_dir_label, 5, 0)

        self.add_localization_button = QtWidgets.QPushButton(self.settings_box)
        self.add_localization_button.setObjectName("add_localization_button")
        self.add_localization_button.setMaximumWidth(200)
        self.add_localization_button.clicked.connect(self.add_locale)
        self.gridLayout.addWidget(self.add_localization_button, 6, 1)
        self.add_localization_label = QtWidgets.QLabel(self.settings_box)
        self.add_localization_label.setObjectName("add_localization_label")
        self.gridLayout.addWidget(self.add_localization_label, 6, 0)

        self.rate_limit_label = QtWidgets.QLabel(get_str('download_video_speed_limit'))
        self.rate_limit_edit = QtWidgets.QLineEdit()
        self.rate_limit_edit.setValidator(QIntValidator(0, 99999))
        self.rate_limit_edit.setMaximumWidth(150)
        self.rate_limit_edit.setText(str(self.old_settings.rate_limit))
        self.gridLayout.addWidget(self.rate_limit_label, 7, 0)
        self.gridLayout.addWidget(self.rate_limit_edit, 7, 1)

        self.choose_video_format_combo_box = FormatChooserComboBox(self)
        self.choose_video_format_combo_box.setGeometry(QtCore.QRect(620, 100, 300, 30))
        self.choose_video_format_combo_box.setObjectName('choose_video_format_combo_box')
        self.choose_video_format_combo_box.setCurrentIndex(self.old_settings.format)
        self.choose_video_format_combo_label = QtWidgets.QLabel(self.settings_box)
        self.choose_video_format_combo_label.setObjectName("choose_video_format_combo_label")
        self.gridLayout.addWidget(self.choose_video_format_combo_label, 8, 0)
        self.gridLayout.addWidget(self.choose_video_format_combo_box, 8, 1)

        self.choose_video_quality_form = ChooseVideoQualityComboBox(self)
        self.choose_video_quality_form.setObjectName('choose_video_quality_form')
        self.choose_video_quality_form.setCurrentIndex(self.old_settings.video_quality)
        self.choose_video_quality_label = QtWidgets.QLabel(self.settings_box)
        self.choose_video_quality_label.setObjectName("choose_video_quality_label")
        self.gridLayout.addWidget(self.choose_video_quality_label, 9, 0)
        self.gridLayout.addWidget(self.choose_video_quality_form, 9, 1)

        self.extension_chooser_combo_box = ExtensionChooserComboBox(self)
        self.extension_chooser_combo_box.setObjectName('choose_extension_quality_form')
        self.choose_video_extension_label = QtWidgets.QLabel(self.settings_box)
        self.choose_video_extension_label.setObjectName("choose_video_extension_label")
        self.extension_chooser_combo_box.setCurrentIndex(self.old_settings.video_extension)
        self.gridLayout.addWidget(self.choose_video_extension_label, 10, 0)
        self.gridLayout.addWidget(self.extension_chooser_combo_box, 10, 1)

        self.retries_label = QtWidgets.QLabel('retries')
        self.retries_edit = QtWidgets.QLineEdit()
        self.retries_edit.setValidator(QIntValidator(0, 100))
        self.retries_edit.setMaximumWidth(150)
        self.retries_edit.setText(str(self.old_settings.retries))
        self.gridLayout.addWidget(self.retries_label, 11, 0)
        self.gridLayout.addWidget(self.retries_edit, 11, 1)

        self.no_check_certificate = QtWidgets.QCheckBox(self)
        self.no_check_certificate.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.no_check_certificate.setObjectName('remove_files_after_upload')
        self.no_check_certificate.setChecked(self.old_settings.no_check_certificate)
        self.no_check_certificate_label = QtWidgets.QLabel(self.settings_box)
        self.no_check_certificate_label.setObjectName("remove_files_after_upload_label")
        self.gridLayout.addWidget(self.no_check_certificate_label, 12, 0)
        self.gridLayout.addWidget(self.no_check_certificate, 12, 1)

        self.audio_quality_label = QtWidgets.QLabel('audio_quality')
        self.audio_quality = QtWidgets.QLineEdit()
        self.audio_quality.setValidator(QIntValidator(1, 9))
        self.audio_quality.setMaximumWidth(150)
        self.audio_quality.setText(str(self.old_settings.audio_quality))
        self.gridLayout.addWidget(self.audio_quality_label, 13, 0)
        self.gridLayout.addWidget(self.audio_quality, 13, 1)

        self.no_cache_dir = QtWidgets.QCheckBox(self)
        self.no_cache_dir.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.no_cache_dir.setObjectName('remove_files_after_upload')
        self.no_cache_dir.setChecked(self.old_settings.no_cache_dir)
        self.no_cache_dir_label = QtWidgets.QLabel(self.settings_box)
        self.no_cache_dir_label.setObjectName("no_cache_dir_label")
        self.gridLayout.addWidget(self.no_cache_dir_label, 14, 0)
        self.gridLayout.addWidget(self.no_cache_dir, 14, 1)

        self.referer_label = QtWidgets.QLabel('referer')
        self.referer = QtWidgets.QLineEdit()
        self.referer.setMaximumWidth(150)
        self.referer.setText(str(self.old_settings.referer))
        self.gridLayout.addWidget(self.referer_label, 15, 0)
        self.gridLayout.addWidget(self.referer, 15, 1)

        self.geo_bypass_country_label = QtWidgets.QLabel('geo_bypass_country')
        self.geo_bypass_country = QtWidgets.QLineEdit()
        self.geo_bypass_country.setMaximumWidth(150)
        self.geo_bypass_country.setText(str(self.old_settings.geo_bypass_country))
        self.gridLayout.addWidget(self.geo_bypass_country_label, 16, 0)
        self.gridLayout.addWidget(self.geo_bypass_country, 16, 1)

        self.keep_fragments = QtWidgets.QCheckBox(self)
        self.keep_fragments.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.keep_fragments.setObjectName('keep_fragments')
        self.keep_fragments.setChecked(self.old_settings.keep_fragments)
        self.keep_fragments_label = QtWidgets.QLabel(self.settings_box)
        self.keep_fragments_label.setObjectName("keep_fragments_label")
        self.gridLayout.addWidget(self.keep_fragments_label, 17, 0)
        self.gridLayout.addWidget(self.keep_fragments, 17, 1)

        self.buffer_size_label = QtWidgets.QLabel('buffer_size_label')
        self.buffer_size = QtWidgets.QLineEdit()
        self.buffer_size.setValidator(QIntValidator(0, 99999))
        self.buffer_size.setMaximumWidth(150)
        self.buffer_size.setText(str(self.old_settings.buffer_size))
        self.gridLayout.addWidget(self.buffer_size_label, 18, 0)
        self.gridLayout.addWidget(self.buffer_size, 18, 1)

        self.write_sub = QtWidgets.QCheckBox(self)
        self.write_sub.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.write_sub.setObjectName('write_sub')
        self.write_sub.setChecked(self.old_settings.write_sub)
        self.write_sub_label = QtWidgets.QLabel(self.settings_box)
        self.write_sub_label.setObjectName("write_sub_label")
        self.gridLayout.addWidget(self.write_sub_label, 19, 0)
        self.gridLayout.addWidget(self.write_sub, 19, 1)

        self.embed_subs = QtWidgets.QCheckBox(self)
        self.embed_subs.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.embed_subs.setObjectName('embed_subs')
        self.embed_subs.setChecked(self.old_settings.embed_subs)
        self.embed_subs_label = QtWidgets.QLabel(self.settings_box)
        self.embed_subs_label.setObjectName("embed_subs_label")
        self.gridLayout.addWidget(self.embed_subs_label, 20, 0)
        self.gridLayout.addWidget(self.embed_subs, 20, 1)

        self.remove_files_after_upload = QtWidgets.QCheckBox(self)
        self.remove_files_after_upload.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.remove_files_after_upload.setObjectName('remove_files_after_upload')
        self.remove_files_after_upload.setChecked(self.old_settings.remove_files_after_upload)
        self.remove_files_after_upload_label = QtWidgets.QLabel(self.settings_box)
        self.remove_files_after_upload_label.setObjectName("remove_files_after_upload_label")
        self.gridLayout.addWidget(self.remove_files_after_upload_label, 21, 0)
        self.gridLayout.addWidget(self.remove_files_after_upload, 21, 1)

        self.events_page_button = QtWidgets.QPushButton(self.settings_box)
        self.events_page_button.setObjectName("events_page_button")
        self.events_page_button.setMaximumWidth(200)
        self.events_page_button.clicked.connect(self.open_events_page)
        self.events_label = QtWidgets.QLabel(self.settings_box)
        self.events_label.setObjectName("add_localization_label")
        self.gridLayout.addWidget(self.events_label, 22, 0)
        self.gridLayout.addWidget(self.events_page_button, 22, 1)

        self.send_crash_notifications = QtWidgets.QCheckBox(self.settings_box)
        self.send_crash_notifications.setObjectName("autostart")
        self.send_crash_notifications.setChecked(self.old_settings.send_crash_notifications)
        self.gridLayout.addWidget(self.send_crash_notifications, 23, 0)

        self.save_password = QtWidgets.QCheckBox(self.settings_box)
        self.save_password.setObjectName("save_password")
        self.save_password.setChecked(self.old_settings.save_password)
        self.gridLayout.addWidget(self.save_password, 24, 0)

        self.save_button = QtWidgets.QPushButton(self.settings_box)
        self.save_button.setObjectName("save_button")
        self.save_button.setMaximumWidth(80)
        self.save_button.clicked.connect(self.on_save)
        self.gridLayout.addWidget(self.save_button, 25, 0)

        self.autostart = QtWidgets.QCheckBox(self.settings_box)
        self.autostart.setObjectName("autostart")
        self.autostart.setChecked(self.old_settings.autostart)
        self.gridLayout.addWidget(self.autostart, 25, 1)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(get_str('settings_page'))
        self.main_settings.setText(f'{get_str("system_settings")}:')
        self.language_label.setText(get_str('language'))
        self.download_strategy_label.setText(get_str('download_strategy'))
        self.pack_count_label.setText(get_str('count_media_for_synchronous_downloading'))
        self.rate_limit_label.setText(get_str('download_speed_limit'))
        self.autostart.setText(get_str('application_autostart'))
        self.save_password.setText(get_str('save_password'))
        self.retries_label.setText(get_str('retries'))
        self.no_check_certificate_label.setText(get_str('no_check_certificate'))
        self.audio_quality_label.setText(get_str('audio_quality'))
        self.no_cache_dir_label.setText(get_str('no_cache_dir'))
        self.referer_label.setText(get_str('referer'))
        self.geo_bypass_country_label.setText(get_str("geo_bypass_country"))
        self.keep_fragments_label.setText(get_str("keep_fragments"))
        self.buffer_size_label.setText(get_str("buffer_size"))
        self.write_sub_label.setText(get_str("write_sub"))
        self.embed_subs_label.setText(get_str("embed_subs"))
        self.remove_files_after_upload_label.setText(get_str('remove_files_after_upload'))
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
        try:
            if self.old_settings.autostart != (self.autostart.checkState() != 0):
                import os

                if os.name.__contains__('Windows'):
                    if self.autostart.checkState() != 0:
                        import winreg

                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0,
                                             winreg.KEY_ALL_ACCESS)
                        winreg.SetValueEx(key, "BuxarVideoUploader", 0, winreg.REG_SZ, f'{os.path.abspath("Application")}.exe')
                        key.Close()
                    else:
                        import winreg

                        winreg.DeleteValue("BuxarVideoUploader")
                else:
                    if self.autostart.checkState() != 0:
                        import subprocess

                        service = f'''
                        [Unit]
                        Description=BuxarVideoUploader
    
                        [Service]
                        ExecStart=.{os.path.abspath("Application")}
                        Restart=always
    
                        [Install]
                        WantedBy=multi-user.target
                        '''

                        with open('/etc/systemd/system/BuxarVideoUploader.service', 'w') as f:
                            f.write(service)

                        subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
                        subprocess.run(['sudo', 'systemctl', 'enable', 'BuxarVideoUploader.service'])
                        subprocess.run(['sudo', 'systemctl', 'start', 'BuxarVideoUploader.service'])
        except:
            log_error(traceback.format_exc())

        self.state_service.save_settings(
            Settings(
                language=self.language_box.currentData(),
                download_strategy=self.download_strategy_box.currentData(),
                download_dir=self.choose_dir_button.text(),
                pack_count=int(self.pack_count_edit.text()),
                rate_limit=int(self.rate_limit_edit.text()),
                send_crash_notifications=self.send_crash_notifications.checkState() != 0,
                video_quality=self.choose_video_quality_form.currentIndex(),
                format=self.choose_video_format_combo_box.currentIndex(),
                remove_files_after_upload=self.remove_files_after_upload.checkState() != 0,
                retries=int(self.retries_edit.text()),
                no_check_certificate=self.no_check_certificate.checkState() != 0,
                audio_quality=int(self.audio_quality.text()),
                no_cache_dir=self.no_cache_dir.checkState() != 0,
                referer=self.referer.text(),
                geo_bypass_country=self.geo_bypass_country.text(),
                keep_fragments=self.keep_fragments.checkState() != 0,
                buffer_size=int(self.buffer_size.text()),
                write_sub=self.write_sub.checkState() != 0,
                embed_subs=self.embed_subs.checkState() != 0))
