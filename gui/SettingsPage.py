import traceback
from os import path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIntValidator

from gui.widgets.AudioQualityComboBox import AudioQualityComboBox
from gui.widgets.VideoQualityComboBox import VideoQualityComboBox
from gui.widgets.ChooseVideoQualityComboBox import ChooseVideoQualityComboBox
from gui.widgets.EventsListForm import EventsListForm
from gui.widgets.ExstensionChooserComboBox import ExtensionChooserComboBox
from gui.widgets.FormatChooserComboBox import FormatChooserComboBox
from model.Settings import Settings
from service.LocalizationService import *
from service.LoggingService import log_error
from service.MailService import MailService
from service.VersionService import VersionService


class SettingsPage(QtWidgets.QDialog):
    state_service = StateService()

    def __init__(self, central_widget):

        super(SettingsPage, self).__init__(central_widget)

        self.setFixedSize(900, 700)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.old_settings = self.state_service.get_settings()
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.setObjectName("Settings")

        self.settings_box = QtWidgets.QWidget()

        self.gridLayout = QtWidgets.QGridLayout(self.settings_box)
        self.scroll.setWidget(self.settings_box)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(-100)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.main_settings = QtWidgets.QLabel()
        self.main_settings.setObjectName("main_settings")
        self.main_settings.setMinimumWidth(200)
        self.main_settings.setMaximumHeight(20)
        self.gridLayout.addWidget(self.main_settings, 1, 0)

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

        self.choose_dir_button = QtWidgets.QPushButton()
        self.choose_dir_button.setObjectName("choose_dir_button")
        self.choose_dir_button.setMaximumWidth(200)
        self.choose_dir_button.clicked.connect(self.pick_new)
        self.gridLayout.addWidget(self.choose_dir_button, 5, 1)
        self.choose_dir_label = QtWidgets.QLabel()
        self.choose_dir_label.setObjectName("choose_dir_label")
        self.gridLayout.addWidget(self.choose_dir_label, 5, 0)

        self.add_localization_button = QtWidgets.QPushButton()
        self.add_localization_button.setObjectName("add_localization_button")
        self.add_localization_button.setMaximumWidth(200)
        self.add_localization_button.clicked.connect(self.add_locale)
        self.gridLayout.addWidget(self.add_localization_button, 6, 1)
        self.add_localization_label = QtWidgets.QLabel()
        self.add_localization_label.setObjectName("add_localization_label")
        self.gridLayout.addWidget(self.add_localization_label, 6, 0)

        self.rate_limit_label = QtWidgets.QLabel(get_str('download_video_speed_limit'))
        self.rate_limit_edit = QtWidgets.QLineEdit()
        self.rate_limit_edit.setValidator(QIntValidator(0, 99999))
        self.rate_limit_edit.setMaximumWidth(150)
        self.rate_limit_edit.setText(str(self.old_settings.rate_limit))
        self.gridLayout.addWidget(self.rate_limit_label, 7, 0)
        self.gridLayout.addWidget(self.rate_limit_edit, 7, 1)

        self.manual_settings = QtWidgets.QCheckBox(self)
        self.manual_settings.setObjectName('write_sub')
        self.manual_settings.setChecked(self.old_settings.manual_settings)
        self.manual_settings_label = QtWidgets.QLabel()
        self.manual_settings_label.setObjectName("write_sub_label")
        self.gridLayout.addWidget(self.manual_settings_label, 8, 0)
        self.gridLayout.addWidget(self.manual_settings, 8, 1)

        self.manual_settings.clicked.connect(self.on_manual_settings_clicked)

        self.video_quality = VideoQualityComboBox(self)
        self.video_quality.setCurrentIndex(self.old_settings.video_quality_str)
        self.video_quality_label = QtWidgets.QLabel()
        self.gridLayout.addWidget(self.video_quality_label, 9, 0)
        self.gridLayout.addWidget(self.video_quality, 9, 1)

        self.audio_quality = AudioQualityComboBox(self)
        self.audio_quality.setCurrentIndex(self.old_settings.audio_quality_str)
        self.audio_quality_label = QtWidgets.QLabel()
        self.gridLayout.addWidget(self.audio_quality_label, 10, 0)
        self.gridLayout.addWidget(self.audio_quality, 10, 1)

        self.choose_video_format_combo_box = FormatChooserComboBox(self)
        self.choose_video_format_combo_box.setObjectName('choose_video_format_combo_box')
        self.choose_video_format_combo_box.setCurrentIndex(self.old_settings.format)
        self.choose_video_format_combo_label = QtWidgets.QLabel()
        self.choose_video_format_combo_label.setObjectName("choose_video_format_combo_label")
        self.gridLayout.addWidget(self.choose_video_format_combo_label, 9, 0)
        self.gridLayout.addWidget(self.choose_video_format_combo_box, 9, 1)

        self.choose_video_quality_form = ChooseVideoQualityComboBox(self)
        self.choose_video_quality_form.setObjectName('choose_video_quality_form')
        self.choose_video_quality_form.setCurrentIndex(self.old_settings.video_quality)
        self.choose_video_quality_label = QtWidgets.QLabel()
        self.choose_video_quality_label.setObjectName("choose_video_quality_label")
        self.gridLayout.addWidget(self.choose_video_quality_label, 10, 0)
        self.gridLayout.addWidget(self.choose_video_quality_form, 10, 1)

        self.audio_bitrate_label = QtWidgets.QLabel('audio_bitrate_label')
        self.audio_bitrate = QtWidgets.QLineEdit()
        self.audio_bitrate.setValidator(QIntValidator(0, 100000))
        self.audio_bitrate.setMaximumWidth(150)
        self.audio_bitrate.setText(str(self.old_settings.audio_bitrate))
        self.gridLayout.addWidget(self.audio_bitrate_label, 11, 0)
        self.gridLayout.addWidget(self.audio_bitrate, 11, 1)

        self.video_bitrate_label = QtWidgets.QLabel('video_bitrate_label')
        self.video_bitrate = QtWidgets.QLineEdit()
        self.video_bitrate.setValidator(QIntValidator(0, 100000))
        self.video_bitrate.setMaximumWidth(150)
        self.video_bitrate.setText(str(self.old_settings.video_bitrate))
        self.gridLayout.addWidget(self.video_bitrate_label, 12, 0)
        self.gridLayout.addWidget(self.video_bitrate, 12, 1)

        self.audio_sampling_rate_label = QtWidgets.QLabel('audio_sampling_rate_label')
        self.audio_sampling_rate = QtWidgets.QLineEdit()
        self.audio_sampling_rate.setValidator(QIntValidator(0, 1000000))
        self.audio_sampling_rate.setMaximumWidth(150)
        self.audio_sampling_rate.setText(str(self.old_settings.audio_sampling_rate))
        self.gridLayout.addWidget(self.audio_sampling_rate_label, 13, 0)
        self.gridLayout.addWidget(self.audio_sampling_rate, 13, 1)

        self.fps_label = QtWidgets.QLabel('fps_label')
        self.fps = QtWidgets.QLineEdit()
        self.fps.setValidator(QIntValidator(0, 1000))
        self.fps.setMaximumWidth(150)
        self.fps.setText(str(self.old_settings.fps))
        self.gridLayout.addWidget(self.fps_label, 14, 0)
        self.gridLayout.addWidget(self.fps, 14, 1)

        self.extension_chooser_combo_box = ExtensionChooserComboBox(self)
        self.extension_chooser_combo_box.setObjectName('choose_extension_quality_form')
        self.choose_video_extension_label = QtWidgets.QLabel()
        self.choose_video_extension_label.setObjectName("choose_video_extension_label")
        self.extension_chooser_combo_box.setCurrentIndex(self.old_settings.video_extension)
        self.gridLayout.addWidget(self.choose_video_extension_label, 15, 0)
        self.gridLayout.addWidget(self.extension_chooser_combo_box, 15, 1)

        self.retries_label = QtWidgets.QLabel('retries')
        self.retries_edit = QtWidgets.QLineEdit()
        self.retries_edit.setValidator(QIntValidator(0, 100))
        self.retries_edit.setMaximumWidth(150)
        self.retries_edit.setText(str(self.old_settings.retries))
        self.gridLayout.addWidget(self.retries_label, 16, 0)
        self.gridLayout.addWidget(self.retries_edit, 16, 1)

        self.no_check_certificate = QtWidgets.QCheckBox(self)
        self.no_check_certificate.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.no_check_certificate.setObjectName('remove_files_after_upload')
        self.no_check_certificate.setChecked(self.old_settings.no_check_certificate)
        self.no_check_certificate_label = QtWidgets.QLabel()
        self.no_check_certificate_label.setObjectName("remove_files_after_upload_label")
        self.gridLayout.addWidget(self.no_check_certificate_label, 17, 0)
        self.gridLayout.addWidget(self.no_check_certificate, 17, 1)

        self.audio_quality_number_label = QtWidgets.QLabel('audio_quality')
        self.audio_quality_number = QtWidgets.QLineEdit()
        self.audio_quality_number.setValidator(QIntValidator(1, 9))
        self.audio_quality_number.setMaximumWidth(150)
        self.audio_quality_number.setText(str(self.old_settings.audio_quality))
        self.gridLayout.addWidget(self.audio_quality_number_label, 18, 0)
        self.gridLayout.addWidget(self.audio_quality_number, 18, 1)

        self.no_cache_dir = QtWidgets.QCheckBox(self)
        self.no_cache_dir.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.no_cache_dir.setObjectName('remove_files_after_upload')
        self.no_cache_dir.setChecked(self.old_settings.no_cache_dir)
        self.no_cache_dir_label = QtWidgets.QLabel()
        self.no_cache_dir_label.setObjectName("no_cache_dir_label")
        self.gridLayout.addWidget(self.no_cache_dir_label, 19, 0)
        self.gridLayout.addWidget(self.no_cache_dir, 19, 1)

        self.referer_label = QtWidgets.QLabel('referer')
        self.referer = QtWidgets.QLineEdit()
        self.referer.setMaximumWidth(150)
        self.referer.setText(str(self.old_settings.referer))
        self.gridLayout.addWidget(self.referer_label, 20, 0)
        self.gridLayout.addWidget(self.referer, 20, 1)

        self.geo_bypass_country_label = QtWidgets.QLabel('geo_bypass_country')
        self.geo_bypass_country = QtWidgets.QLineEdit()
        self.geo_bypass_country.setMaximumWidth(150)
        self.geo_bypass_country.setText(str(self.old_settings.geo_bypass_country))
        self.gridLayout.addWidget(self.geo_bypass_country_label, 21, 0)
        self.gridLayout.addWidget(self.geo_bypass_country, 21, 1)

        self.keep_fragments = QtWidgets.QCheckBox(self)
        self.keep_fragments.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.keep_fragments.setObjectName('keep_fragments')
        self.keep_fragments.setChecked(self.old_settings.keep_fragments)
        self.keep_fragments_label = QtWidgets.QLabel()
        self.keep_fragments_label.setObjectName("keep_fragments_label")
        self.gridLayout.addWidget(self.keep_fragments_label, 22, 0)
        self.gridLayout.addWidget(self.keep_fragments, 22, 1)

        self.buffer_size_label = QtWidgets.QLabel('buffer_size_label')
        self.buffer_size = QtWidgets.QLineEdit()
        self.buffer_size.setValidator(QIntValidator(0, 99999))
        self.buffer_size.setMaximumWidth(150)
        self.buffer_size.setText(str(self.old_settings.buffer_size))
        self.gridLayout.addWidget(self.buffer_size_label, 23, 0)
        self.gridLayout.addWidget(self.buffer_size, 23, 1)

        self.write_sub = QtWidgets.QCheckBox(self)
        self.write_sub.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.write_sub.setObjectName('write_sub')
        self.write_sub.setChecked(self.old_settings.write_sub)
        self.write_sub_label = QtWidgets.QLabel()
        self.write_sub_label.setObjectName("write_sub_label")
        self.gridLayout.addWidget(self.write_sub_label, 24, 0)
        self.gridLayout.addWidget(self.write_sub, 24, 1)

        self.embed_subs = QtWidgets.QCheckBox(self)
        self.embed_subs.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.embed_subs.setObjectName('embed_subs')
        self.embed_subs.setChecked(self.old_settings.embed_subs)
        self.embed_subs_label = QtWidgets.QLabel()
        self.embed_subs_label.setObjectName("embed_subs_label")
        self.gridLayout.addWidget(self.embed_subs_label, 25, 0)
        self.gridLayout.addWidget(self.embed_subs, 25, 1)

        self.remove_files_after_upload = QtWidgets.QCheckBox(self)
        self.remove_files_after_upload.setGeometry(QtCore.QRect(620, 200, 30, 30))
        self.remove_files_after_upload.setObjectName('remove_files_after_upload')
        self.remove_files_after_upload.setChecked(self.old_settings.remove_files_after_upload)
        self.remove_files_after_upload_label = QtWidgets.QLabel()
        self.remove_files_after_upload_label.setObjectName("remove_files_after_upload_label")
        self.gridLayout.addWidget(self.remove_files_after_upload_label, 26, 0)
        self.gridLayout.addWidget(self.remove_files_after_upload, 26, 1)

        self.events_page_button = QtWidgets.QPushButton()
        self.events_page_button.setObjectName("events_page_button")
        self.events_page_button.setMaximumWidth(200)
        self.events_page_button.clicked.connect(self.open_events_page)
        self.events_label = QtWidgets.QLabel()
        self.events_label.setObjectName("add_localization_label")
        self.gridLayout.addWidget(self.events_label, 27, 0)
        self.gridLayout.addWidget(self.events_page_button, 27, 1)

        self.debug_browser = QtWidgets.QCheckBox()
        self.debug_browser.setObjectName("send_crash_notifications")
        self.debug_browser.setChecked(self.old_settings.debug_browser)
        self.gridLayout.addWidget(self.debug_browser, 28, 0)

        self.send_crash_notifications = QtWidgets.QCheckBox()
        self.send_crash_notifications.setObjectName("send_crash_notifications")
        self.send_crash_notifications.setChecked(self.old_settings.send_crash_notifications)
        self.gridLayout.addWidget(self.send_crash_notifications, 29, 0)

        self.save_password = QtWidgets.QCheckBox()
        self.save_password.setObjectName("save_password")
        self.save_password.setChecked(self.old_settings.save_password)
        self.gridLayout.addWidget(self.save_password, 30, 0)

        self.enable_autostart = QtWidgets.QCheckBox()
        self.enable_autostart.setObjectName("enable_autostart")
        self.enable_autostart.setChecked(self.old_settings.enable_autostart)
        self.gridLayout.addWidget(self.enable_autostart, 31, 0)

        self.clean_log_button = QtWidgets.QPushButton()
        self.clean_log_button.setObjectName("clean_log")
        self.clean_log_button.setMaximumWidth(160)
        self.clean_log_button.clicked.connect(self.on_clean_log)
        self.gridLayout.addWidget(self.clean_log_button, 32, 0)

        self.send_notifications_button = QtWidgets.QPushButton()
        self.send_notifications_button.setObjectName("send_notifications")
        self.send_notifications_button.setMaximumWidth(160)
        self.send_notifications_button.clicked.connect(self.on_send)
        self.gridLayout.addWidget(self.send_notifications_button, 33, 0)

        self.save_button = QtWidgets.QPushButton()
        self.save_button.setObjectName("save_button")
        self.save_button.setMaximumWidth(80)
        self.save_button.clicked.connect(self.on_save)
        self.gridLayout.addWidget(self.save_button, 34, 0)

        self.autostart = QtWidgets.QCheckBox()
        self.autostart.setObjectName("autostart")
        self.autostart.setChecked(self.old_settings.autostart)
        self.gridLayout.addWidget(self.autostart, 34, 1)

        if self.old_settings.manual_settings is False:
            self.audio_quality_number_label.hide()
            self.audio_quality_number.hide()
            self.choose_video_quality_form.hide()
            self.choose_video_quality_label.hide()
            self.choose_video_format_combo_box.hide()
            self.choose_video_format_combo_label.hide()
            self.choose_video_extension_label.hide()
            self.extension_chooser_combo_box.hide()
            self.video_bitrate.hide()
            self.video_bitrate_label.hide()
            self.audio_bitrate.hide()
            self.audio_bitrate_label.hide()
            self.audio_sampling_rate.hide()
            self.audio_sampling_rate_label.hide()
            self.fps.hide()
            self.fps_label.hide()
        else:
            self.audio_quality.hide()
            self.audio_quality_label.hide()
            self.video_quality.hide()
            self.video_quality_label.hide()

        self.layout.addWidget(self.scroll)
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
        self.audio_quality_number_label.setText(get_str('audio_quality'))
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
        self.debug_browser.setText(get_str('debug_browser'))
        self.add_localization_label.setText(get_str('add_localization'))
        self.choose_dir_button.setText(self.old_settings.download_dir)
        self.clean_log_button.setText(get_str('clean_log'))
        self.send_notifications_button.setText(get_str('report_bug'))
        self.enable_autostart.setText(get_str('enable_autostart'))
        self.save_button.setText(get_str('save'))
        self.manual_settings_label.setText(get_str('manual_settings'))
        self.video_quality_label.setText(get_str('video_quality'))
        self.audio_quality_label.setText(get_str('audio_quality_str'))
        self.choose_video_quality_label.setText(get_str('video_quality'))
        self.choose_video_extension_label.setText(get_str('video_extension'))
        self.choose_video_format_combo_label.setText(get_str('download_format'))
        self.video_bitrate_label.setText(get_str('video_bitrate'))
        self.audio_bitrate_label.setText(get_str('audio_bitrate'))
        self.audio_sampling_rate_label.setText(get_str('audio_sampling_rate'))
        self.fps_label.setText(get_str('fps'))

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

    def on_manual_settings_clicked(self):
        if self.manual_settings.checkState() == 0:
            self.audio_quality_number_label.hide()
            self.audio_quality_number.hide()
            self.choose_video_quality_form.hide()
            self.choose_video_quality_label.hide()
            self.choose_video_format_combo_box.hide()
            self.choose_video_format_combo_label.hide()
            self.choose_video_extension_label.hide()
            self.extension_chooser_combo_box.hide()
            self.video_bitrate.hide()
            self.video_bitrate_label.hide()
            self.audio_bitrate.hide()
            self.audio_bitrate_label.hide()
            self.audio_sampling_rate.hide()
            self.audio_sampling_rate_label.hide()
            self.fps.hide()
            self.fps_label.hide()
            self.audio_quality.show()
            self.audio_quality_label.show()
            self.video_quality.show()
            self.video_quality_label.show()
        else:
            self.audio_quality_number_label.show()
            self.audio_quality_number.show()
            self.choose_video_quality_form.show()
            self.choose_video_quality_label.show()
            self.choose_video_format_combo_box.show()
            self.choose_video_format_combo_label.show()
            self.choose_video_extension_label.show()
            self.extension_chooser_combo_box.show()
            self.video_bitrate.show()
            self.video_bitrate_label.show()
            self.audio_bitrate.show()
            self.audio_bitrate_label.show()
            self.audio_sampling_rate.show()
            self.audio_sampling_rate_label.show()
            self.fps.show()
            self.fps_label.show()
            self.audio_quality.hide()
            self.audio_quality_label.hide()
            self.video_quality.hide()
            self.video_quality_label.hide()

    def on_clean_log(self):
        msg = QtWidgets.QMessageBox(self)

        try:
            open("log/BuxarVideoUploader.log", "w").close()
            msg.setWindowTitle(get_str('ok'))
            msg.setText(get_str('clean_successfully'))
        except:
            msg.setWindowTitle('error')
            msg.setText(get_str('error'))
            log_error(traceback.format_exc())

        msg.exec_()

    def on_send(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(get_str('error'))

        if self.state_service.is_error_appeared():
            try:
                MailService().send_log()
                msg.setText(get_str('send_successfully'))
                self.state_service.set_error_status(False)
            except:
                msg.setText(get_str('send_failed'))
        else:
            msg.setText(get_str('already_sent'))
        msg.exec_()

    def on_save(self):

        # if self.old_settings.download_strategy != self.download_strategy_box.currentIndex() \
        #         or self.old_settings.pack_count != int(self.pack_count_edit.text()):
        #     msg = QtWidgets.QMessageBox()
        #     msg.setText(get_str('for_applying_strategy_settings_need_to_restart'))
        #     msg.exec_()

        if self.old_settings.language != self.language_box.currentData():
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('for_applying_localization_settings_need_to_restart'))
            msg.exec_()
        try:
            if self.old_settings.autostart != (self.autostart.checkState() != 0):
                import os

                if os.name == 'nt':

                    from pyshortcuts import make_shortcut
                    import os
                    if self.autostart.checkState() != 0:
                        make_shortcut(f'{os.path.sys.path[0]}\\Application.exe',
                                      name='BuxarVideoUploader',
                                      icon=f'{os.path.sys.path[0]}\\icon.png',
                                      working_dir=f'{os.path.sys.path[0]}',
                                      folder='C:\\Users\\dendil\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
                    else:
                        os.remove(
                            'C:\\Users\\dendil\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\BuxarVideoUploader.lnk')

                else:
                    import subprocess

                    if self.autostart.checkState() != 0:

                        service = f'''
[Unit]
[Desktop Entry]
Version=1.0.0.0
GenericName=BuxarVideoUploader
Name=BuxarVideoUploader
Comment=BuxarVideoUploader
Icon=/usr/share/BuxarVideoUploader/dist/Application/icon.png
Exec=sh -c "cd /usr/share/BuxarVideoUploader/dist/Application && ./Application"
Terminal=false
StartupWMClass=Application
Categories=Network;FileTransfer;
Type=Application
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
                        '''

                        if os.path.exists(f'{path.normpath(path.expanduser("~/.config/"))}/autostart') is False:
                            os.makedirs(f'{path.normpath(path.expanduser("~/.config/"))}/autostart')

                        with open(f'{path.normpath(path.expanduser("~/.config/"))}/autostart/BuxarVideoUploader.desktop', 'x') as f:
                            f.write(service)
                    else:
                        os.remove(f'{path.normpath(path.expanduser("~/.config/"))}/autostart/BuxarVideoUploader.desktop')

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
                audio_quality=int(self.audio_quality_number.text()),
                no_cache_dir=self.no_cache_dir.checkState() != 0,
                referer=self.referer.text(),
                geo_bypass_country=self.geo_bypass_country.text(),
                keep_fragments=self.keep_fragments.checkState() != 0,
                buffer_size=int(self.buffer_size.text()),
                write_sub=self.write_sub.checkState() != 0,
                embed_subs=self.embed_subs.checkState() != 0,
                manual_settings=self.manual_settings.checkState() != 0,
                audio_bitrate=self.audio_bitrate.text(),
                audio_sampling_rate=self.audio_sampling_rate.text(),
                video_bitrate=self.video_bitrate.text(),
                fps=self.fps.text(),
                audio_quality_str=self.audio_quality.currentIndex(),
                video_quality_str=self.video_quality.currentIndex(),
                ffmpeg=self.old_settings.ffmpeg,
                encrypted_key=self.old_settings.encrypted_key,
                user_mail=self.old_settings.user_mail,
                video_extension=self.extension_chooser_combo_box.currentIndex(),
                debug_browser=self.debug_browser.checkState() != 0,
                autostart=self.autostart.checkState() != 0,
                enable_autostart=self.enable_autostart.checkState() != 0))
