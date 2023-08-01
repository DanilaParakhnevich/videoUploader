import asyncio
import datetime
import uuid
from functools import partial

from PyQt5.QtGui import QIntValidator
from dateutil.relativedelta import relativedelta

from PyQt5 import QtCore, QtWidgets

from gui.widgets.AddDownloadQueueViaLinkForm import AddDownloadQueueViaLinkForm
from gui.widgets.AgreeToDownloadDialog import AgreeToDownloadDialog
from gui.widgets.AgreeToRepeatDownloadDialog import AgreeToRepeatDownloadDialog
from gui.widgets.AudioQualityComboBox import AudioQualityComboBox
from gui.widgets.ChooseVideoQualityComboBox import ChooseVideoQualityComboBox
from gui.widgets.ExstensionChooserComboBox import ExtensionChooserComboBox
from gui.widgets.FormatChooserComboBox import FormatChooserComboBox
from gui.widgets.ShowErrorDialog import ShowErrorDialog
from gui.widgets.TypeStrForm import TypeStrForm
from gui.widgets.VideoQualityComboBox import VideoQualityComboBox
from model.Event import Event
from model.LoadQueuedMedia import LoadQueuedMedia
from model.Hosting import Hosting
from model.Tab import TabModel
from gui.widgets.ChannelComboBox import ChannelComboBox
from gui.widgets.ChooseAccountForm import ChooseAccountForm
from gui.widgets.UploadAfterDownloadForm import UploadAfterDownloadForm
from gui.widgets.LoadingButton import AnimatedButton
from model.UploadQueueMedia import UploadQueueMedia
from service.EventService import EventService
from service.LocalizationService import *
from service.MailService import MailService
from service.QueueMediaService import QueueMediaService
from threading import Thread
from service.LoggingService import *
import traceback

from service.videohosting_service.exception.DescriptionIsTooLongException import DescriptionIsTooLongException
from service.videohosting_service.exception.FileFormatException import FileFormatException
from service.videohosting_service.exception.FileSizeException import FileSizeException
from service.videohosting_service.exception.NameIsTooLongException import NameIsTooLongException
from service.videohosting_service.exception.VideoDurationException import VideoDurationException


# Класс страницы выгрузки видео с видеохостингов
class LoadPageWidget(QtWidgets.QTabWidget):
    state_service = StateService()
    queue_media_service = QueueMediaService()
    tab_models = state_service.get_last_tabs()  # Используются для хранения легких и необходимых данных
    tables = list()
    tabs = list()
    current_table_index = 0

    def __init__(self, central_widget):

        super(LoadPageWidget, self).__init__(central_widget)

        self.setObjectName("load_page")

        self.tabCloseRequested.connect(self.remove_tab)
        self.setMovable(True)
        self.setTabsClosable(True)

        add_button = QtWidgets.QToolButton()
        add_button.setObjectName("add_button")
        add_button.setText("+")

        add_button.clicked.connect(self.create_empty_tab)

        self.addTab(QtWidgets.QLabel("Add tabs by pressing \"+\""), "")
        self.setTabEnabled(0, False)

        self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, add_button)
        self.currentChanged.connect(self.set_current_table)
        self.first_start = True
        if len(self.tab_models) == 0:
            self.create_empty_tab()
        else:
            for tab in self.tab_models:
                self.create_tab(tab.tab_name, tab.channel, tab.format[0], tab.video_quality[0], tab.video_extension[0],
                                tab.remove_files_after_upload, tab.download_dir if hasattr(tab, 'download_dir')
                                else self.state_service.get_settings().download_dir, tab.manual_settings,
                                tab.video_quality_str, tab.audio_quality_str, tab.audio_bitrate, tab.video_bitrate,
                                tab.audio_sampling_rate, tab.fps, tab.video_list)

        self.first_start = False

        self.setCurrentIndex(0)
        self.event_service = EventService()

    def remove_tab(self, index):
        self.tab_models.pop(index)
        self.tables.pop(index)
        self.tabs.pop(index)
        self.removeTab(index)

        self.state_service.save_tabs_state(self.tab_models)

    def create_empty_tab(self):
        channels = self.state_service.get_channels()
        settings = self.state_service.get_settings()
        if len(channels) == 0:
            return self.create_tab(None, None, settings.format, settings.video_quality, settings.video_extension,
                                   settings.remove_files_after_upload, settings.download_dir, settings.manual_settings,
                                   settings.video_quality_str, settings.audio_quality_str, settings.audio_bitrate,
                                   settings.video_bitrate, settings.audio_sampling_rate, settings.fps, list())
        else:
            return self.create_tab(None, channels.__getitem__(0), settings.format, settings.video_quality,
                                   settings.video_extension, settings.remove_files_after_upload, settings.download_dir,
                                   settings.manual_settings, settings.video_quality_str, settings.audio_quality_str,
                                   settings.audio_bitrate, settings.video_bitrate, settings.audio_sampling_rate, settings.fps, list())

    # Этот метод добавляет новую вкладку, либо вкладку по известным данным из tab_models
    def create_tab(self, name, selected_channel, format_index, video_quality_index, video_extension,
                   remove_files_after_upload,
                   download_dir, manual_settings,
                   video_quality, audio_quality,
                   audio_bitrate, video_bitrate,
                   audio_sampling_rate, fps,
                   video_list=None):

        if video_list is None:
            video_list = list()
        tab = QtWidgets.QWidget()
        tab.setObjectName("Tab.py")

        tab.channel_box = ChannelComboBox(tab, selected_channel)

        tab.channel_box.setObjectName("channel_box")
        tab.add_button = AnimatedButton(tab)
        tab.add_button.setObjectName("add_button")
        tab.add_media_to_query_button = QtWidgets.QPushButton(tab)
        tab.add_media_to_query_button.setObjectName('add_media_to_query_button')
        tab.add_by_link_button = AnimatedButton(tab)
        tab.add_by_link_button.setObjectName("add_button")
        tab.add_by_link_button.setText(get_str('add_download_single_video_by_link'))
        tab.manual_settings = QtWidgets.QCheckBox(tab)
        tab.manual_settings.setChecked(manual_settings)

        def on_manual_settings_clicked():
            if tab.manual_settings.checkState() != 0:
                tab.choose_video_quality_form.show()
                tab.extension_chooser_combo_box.show()
                tab.video_bitrate.show()
                tab.video_bitrate_label.show()
                tab.audio_bitrate.show()
                tab.audio_bitrate_label.show()
                tab.audio_sampling_rate.show()
                tab.audio_sampling_rate_label.show()
                tab.fps.show()
                tab.fps_label.show()
                tab.audio_quality_label.hide()
                tab.audio_quality.hide()
                tab.video_quality.hide()
                tab.video_quality_label.hide()
            else:
                tab.choose_video_quality_form.hide()
                tab.extension_chooser_combo_box.hide()
                tab.video_bitrate.hide()
                tab.video_bitrate_label.hide()
                tab.audio_bitrate.hide()
                tab.audio_bitrate_label.hide()
                tab.audio_sampling_rate.hide()
                tab.audio_sampling_rate_label.hide()
                tab.fps.hide()
                tab.fps_label.hide()
                tab.audio_quality_label.show()
                tab.audio_quality.show()
                tab.video_quality.show()
                tab.video_quality_label.show()
            self.resizeEvent(None)
            if self.current_table_index is not None and tab in self.tabs:
                self.tab_models[self.current_table_index].manual_settings = tab.manual_settings.checkState() != 0
                self.state_service.save_tabs_state(self.tab_models)

        tab.manual_settings.clicked.connect(on_manual_settings_clicked)

        tab.manual_settings_label = QtWidgets.QLabel(tab)
        tab.manual_settings_label.setObjectName("write_sub_label")
        tab.manual_settings_label.setText(get_str('manual_settings'))
        tab.video_quality = VideoQualityComboBox(tab)
        tab.video_quality.currentIndexChanged.connect(self.on_video_quality_changed)
        tab.video_quality.setCurrentIndex(video_quality)
        tab.video_quality_label = QtWidgets.QLabel(tab)
        tab.video_quality_label.setText(get_str('video_quality'))
        tab.audio_quality = AudioQualityComboBox(tab)
        tab.audio_quality.currentIndexChanged.connect(self.on_audio_quality_changed)
        tab.audio_quality.setCurrentIndex(audio_quality)
        tab.audio_quality_label = QtWidgets.QLabel(tab)
        tab.audio_quality_label.setText(get_str('audio_quality_str'))
        tab.choose_video_format_combo_box = FormatChooserComboBox(tab)
        tab.choose_video_format_combo_box.setObjectName('choose_video_format_combo_box')
        tab.choose_video_format_combo_box.setCurrentIndex(format_index)
        tab.choose_video_format_combo_box.currentIndexChanged.connect(self.on_video_format_changed)
        tab.choose_video_quality_form = ChooseVideoQualityComboBox(tab)
        tab.choose_video_quality_form.setObjectName('choose_video_quality_form')
        tab.choose_video_quality_form.setCurrentIndex(video_quality_index)
        tab.choose_video_quality_form.currentIndexChanged.connect(self.on_video_resolution_changed)
        tab.extension_chooser_combo_box = ExtensionChooserComboBox(tab)
        tab.extension_chooser_combo_box.setObjectName('choose_video_quality_form')
        tab.extension_chooser_combo_box.setCurrentIndex(video_extension)
        tab.extension_chooser_combo_box.currentIndexChanged.connect(self.on_video_extension_changed)
        tab.audio_bitrate_label = QtWidgets.QLabel(tab)
        tab.audio_bitrate_label.setText(get_str('audio_bitrate'))
        tab.audio_bitrate = QtWidgets.QLineEdit(tab)
        tab.audio_bitrate.textChanged.connect(self.on_audio_bitrate_changed)
        tab.audio_bitrate.setValidator(QIntValidator(0, 100000))
        tab.audio_bitrate.setMaximumWidth(150)
        tab.audio_bitrate.setText(str(audio_bitrate))
        tab.video_bitrate_label = QtWidgets.QLabel(tab)
        tab.video_bitrate_label.setText(get_str('video_bitrate'))
        tab.video_bitrate = QtWidgets.QLineEdit(tab)
        tab.video_bitrate.textChanged.connect(self.on_video_bitrate_changed)
        tab.video_bitrate.setValidator(QIntValidator(0, 100000))
        tab.video_bitrate.setMaximumWidth(150)
        tab.video_bitrate.setText(str(video_bitrate))
        tab.audio_sampling_rate_label = QtWidgets.QLabel(tab)
        tab.audio_sampling_rate_label.setText(get_str('audio_sampling_rate'))
        tab.audio_sampling_rate = QtWidgets.QLineEdit(tab)
        tab.audio_sampling_rate.textChanged.connect(self.on_audio_sampling_rate_changed)
        tab.audio_sampling_rate.setValidator(QIntValidator(0, 1000000))
        tab.audio_sampling_rate.setMaximumWidth(150)
        tab.audio_sampling_rate.setText(str(audio_sampling_rate))
        tab.fps_label = QtWidgets.QLabel(tab)
        tab.fps_label.setText(get_str('fps'))
        tab.fps = QtWidgets.QLineEdit(tab)
        tab.fps.textChanged.connect(self.on_fps_changed)
        tab.fps.setValidator(QIntValidator(0, 1000))
        tab.fps.setMaximumWidth(150)
        tab.fps.setText(str(fps))
        tab.choose_dir_button = QtWidgets.QPushButton(tab)
        tab.choose_dir_button.setObjectName("choose_dir_button")
        if download_dir == '..':
            tab.choose_dir_button.setText(get_str('choose_the_dir'))
        else:
            tab.choose_dir_button.setText(download_dir)

        def pick_new():
            sorter = QtCore.QSortFilterProxyModel()
            sorter.setDynamicSortFilter(True)

            dialog = QtWidgets.QFileDialog()
            dialog.setProxyModel(sorter)
            folder_path = dialog.getExistingDirectory(None, get_str('choose_dir'))
            if folder_path != '':
                self.tab_models[self.current_table_index].download_dir = folder_path
                self.state_service.save_tabs_state(self.tab_models)
                tab.choose_dir_button.setText(folder_path)

        tab.choose_dir_button.clicked.connect(pick_new)
        tab.remove_files_after_upload = QtWidgets.QCheckBox(tab)
        tab.remove_files_after_upload.setObjectName('remove_files_after_upload')
        tab.remove_files_after_upload.setChecked(remove_files_after_upload)
        tab.remove_files_after_upload.clicked.connect(self.on_remove_files_after_upload_changed)
        tab.remove_files_after_upload_label = QtWidgets.QLabel(tab)
        tab.remove_files_after_upload_label.setText(get_str('remove_files_after_upload'))
        tab.remove_files_after_upload_label.setObjectName('remove_files_after_upload_label')

        tab.reset_tab_settings_button = QtWidgets.QPushButton(tab)
        tab.reset_tab_settings_button.setObjectName("reset_tab_settings_button")
        tab.reset_tab_settings_button.setText(get_str('reset_from_settings'))
        tab.reset_tab_settings_button.clicked.connect(self.reset_tab_settings)

        tab.choose_dir_button.clicked.connect(pick_new)

        def on_add():
            form = AddDownloadQueueViaLinkForm(self, self.tab_models[self.current_table_index].format[0],
                                               self.tab_models[self.current_table_index].video_quality[1],
                                               self.tab_models[self.current_table_index].video_extension[1],
                                               self.tab_models[self.current_table_index].remove_files_after_upload,
                                               manual_settings=self.tab_models[self.current_table_index].manual_settings,
                                               video_bitrate=self.tab_models[self.current_table_index].video_bitrate,
                                               audio_bitrate=self.tab_models[self.current_table_index].audio_bitrate,
                                               video_quality_str=self.tab_models[self.current_table_index].video_quality_str,
                                               audio_quality_str=self.tab_models[self.current_table_index].audio_quality_str,
                                               fps=self.tab_models[self.current_table_index].fps,
                                               audio_sampling_rate=self.tab_models[self.current_table_index].audio_sampling_rate)
            form.exec_()

            if form.passed is True:
                queue_media = LoadQueuedMedia(media_id=str(uuid.uuid4()),
                                              url=form.link,
                                              hosting=form.hosting.name,
                                              status=0,
                                              upload_after_download=form.upload_on,
                                              account=form.account,
                                              video_size=form.video_size,
                                              format=tab.choose_video_format_combo_box.currentData(),
                                              video_quality=tab.choose_video_quality_form.currentData(),
                                              video_extension=tab.extension_chooser_combo_box.currentData(),
                                              remove_files_after_upload=tab.remove_files_after_upload.isChecked(),
                                              upload_date=datetime.datetime.now(),
                                              upload_targets=form.upload_targets,
                                              title=form.title,
                                              description=form.description,
                                              download_dir=tab.choose_dir_button.text() if tab.choose_dir_button.text() != get_str('choose_the_dir') else os.path.abspath(os.path.curdir),
                                              manual_settings=self.tab_models[self.current_table_index].manual_settings,
                                              video_quality_str=self.tab_models[
                                                  self.current_table_index].video_quality_str,
                                              audio_quality_str=self.tab_models[
                                                  self.current_table_index].audio_quality_str,
                                              audio_bitrate=self.tab_models[self.current_table_index].audio_bitrate,
                                              video_bitrate=self.tab_models[self.current_table_index].video_bitrate,
                                              fps=self.tab_models[self.current_table_index].fps,
                                              audio_sampling_rate=self.tab_models[
                                                  self.current_table_index].audio_sampling_rate)

                self.queue_media_service.add_to_the_download_queue(list([queue_media]))

        tab.add_by_link_button.clicked.connect(on_add)

        tab.table_widget = QtWidgets.QTableWidget(tab)
        tab.table_widget.setObjectName("table_widget")
        tab.table_widget.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        tab.table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        tab.table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        tab.table_widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        tab.table_widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        tab.table_widget.setHorizontalHeaderItem(4, item)
        tab.table_widget.horizontalHeader().sectionClicked.connect(self.section_clicked)
        tab.table_widget.horizontalHeader().sectionResized.connect(self.section_resized)
        tab.table_widget.itemClicked.connect(partial(self.on_clicked, len(self.tabs)))
        index = 0

        for video in video_list:
            tab.table_widget.insertRow(index)

            item1 = QtWidgets.QTableWidgetItem(video.name)
            item2 = QtWidgets.QTableWidgetItem(video.url)
            item3 = QtWidgets.QTableWidgetItem(video.date)
            item4 = QtWidgets.QTableWidgetItem()
            item4.setFlags(QtCore.Qt.ItemIsUserCheckable |
                           QtCore.Qt.ItemIsEnabled)
            item4.setCheckState(QtCore.Qt.Checked if hasattr(video, 'checked') and video.checked else 0)

            is_downloaded = get_str('yes') \
                if self.state_service.get_download_queue_media_by_url(video.url) is not None else get_str('no')

            item5 = QtWidgets.QTableWidgetItem(is_downloaded)

            tab.table_widget.setItem(index, 0, item1)
            tab.table_widget.setItem(index, 1, item2)
            tab.table_widget.setItem(index, 2, item3)
            tab.table_widget.setItem(index, 3, item4)
            tab.table_widget.setItem(index, 4, item5)

            index += 1

        self.insertTab(len(self.tables), tab, "")

        tab.add_button.setText(get_str('get'))
        tab.add_button.clicked.connect(lambda: self.create_daemon_for_getting_video_list(tab.add_button))
        tab.add_media_to_query_button.setObjectName("download_button")
        tab.add_media_to_query_button.setText(get_str('add_to_the_queue'))
        item = tab.table_widget.horizontalHeaderItem(0)
        item.setText(get_str("name"))
        item = tab.table_widget.horizontalHeaderItem(1)
        item.setText(get_str("link"))
        item = tab.table_widget.horizontalHeaderItem(2)
        item.setText(get_str("date"))
        item = tab.table_widget.horizontalHeaderItem(3)
        item.setText(get_str("is_download"))
        item = tab.table_widget.horizontalHeaderItem(4)
        item.setText(get_str("is_downloaded"))

        # Тут определяется, существующая вкладка ли
        if name:
            self.setTabText(self.indexOf(tab), name)
        else:
            # Если нет, то даем ей кастомное имя
            index = len(self.tab_models) + 1

            while True:
                val = True
                for i in range(len(self.tab_models) + 1):
                    if self.tabText(i).endswith(f' {index}'):
                        index += 1
                        val = False
                        break
                if val:
                    break
            tab_name = f'{get_str("tab")} {index}'
            self.setTabText(self.indexOf(tab), tab_name)

            self.tab_models.append(
                TabModel(tab_name, '', Hosting.Youtube.name,
                         [tab.choose_video_format_combo_box.currentIndex(),
                          tab.choose_video_format_combo_box.currentData()],
                         [tab.choose_video_quality_form.currentIndex(), tab.choose_video_quality_form.currentData()],
                         [tab.extension_chooser_combo_box.currentIndex(),
                          tab.extension_chooser_combo_box.currentData()],
                         tab.remove_files_after_upload.checkState() != 0,
                         self.state_service.get_settings().download_dir))
            self.state_service.save_tabs_state(self.tab_models)
        self.tables.append(tab.table_widget)

        on_manual_settings_clicked()

        tab.add_media_to_query_button.clicked.connect(self.on_add_media_to_query)
        tab.channel_box.currentTextChanged.connect(self.on_channel_changed)
        tab.video_list = video_list
        self.tabs.append(tab)
        self.resizeEvent(None)

    def on_clicked(self, tab_index, item):
        if item.column() == 3:
            self.tab_models[tab_index].video_list[item.row()].checked = True if item.checkState() == 2 else False
            self.state_service.save_tabs_state(self.tab_models)

    def set_current_table(self, index):
        self.current_table_index = index

    change = True

    def section_resized(self, index):
        if hasattr(self, 'current_table_index') and len(self.tabs) > self.current_table_index and self.change:
            coef_x = self.parent().width() / 950

            name = self.tabText(self.current_table_index)

            self.state_service.save_tab_column_weight(name, index, int(
                self.tabs[self.current_table_index].table_widget.columnWidth(index) / coef_x))

    def section_clicked(self, index):
        if index == 3:

            if self.tables[self.current_table_index].rowCount() > 0:
                to_set = QtCore.Qt.Checked if self.tables[self.current_table_index].item(0, 3).checkState() == 0 else 0

            for index in range(0, self.tables[self.current_table_index].rowCount()):
                self.tables[self.current_table_index].item(index, 3).setCheckState(to_set)

    def reset_tab_settings(self):
        tab_model = self.tab_models[self.current_table_index]

        settings = self.state_service.get_settings()

        self.on_video_format_changed(settings.format)
        self.on_video_quality_changed(settings.video_quality)
        self.on_video_extension_changed(settings.video_extension)
        tab_model.remove_files_after_upload = settings.remove_files_after_upload
        tab_model.download_dir = settings.download_dir

        tab = self.tabs[self.current_table_index]

        tab.choose_video_format_combo_box.setCurrentIndex(tab_model.format[0])
        tab.choose_video_quality_form.setCurrentIndex(tab_model.video_quality[0])
        tab.extension_chooser_combo_box.setCurrentIndex(tab_model.video_extension[0])
        if tab_model.download_dir == '..':
            tab.choose_dir_button.setText(get_str('choose_the_dir'))
        else:
            tab.choose_dir_button.setText(tab_model.download_dir)

        tab.manual_settings.setChecked(settings.manual_settings)
        tab.video_quality.setCurrentIndex(settings.video_quality_str)
        tab.audio_quality.setCurrentIndex(settings.audio_quality_str)
        tab.audio_bitrate.setText(str(settings.audio_bitrate))
        tab.video_bitrate.setText(str(settings.video_bitrate))
        tab.fps.setText(str(settings.fps))
        tab.audio_sampling_rate.setText(str(settings.audio_sampling_rate))

        if tab.manual_settings.checkState() != 0:
            tab.choose_video_quality_form.show()
            tab.extension_chooser_combo_box.show()
            tab.video_bitrate.show()
            tab.video_bitrate_label.show()
            tab.audio_bitrate.show()
            tab.audio_bitrate_label.show()
            tab.audio_sampling_rate.show()
            tab.audio_sampling_rate_label.show()
            tab.fps.show()
            tab.fps_label.show()
            tab.audio_quality_label.hide()
            tab.audio_quality.hide()
            tab.video_quality.hide()
            tab.video_quality_label.hide()
        else:
            tab.choose_video_quality_form.hide()
            tab.extension_chooser_combo_box.hide()
            tab.video_bitrate.hide()
            tab.video_bitrate_label.hide()
            tab.audio_bitrate.hide()
            tab.audio_bitrate_label.hide()
            tab.audio_sampling_rate.hide()
            tab.audio_sampling_rate_label.hide()
            tab.fps.hide()
            tab.fps_label.hide()
            tab.audio_quality_label.show()
            tab.audio_quality.show()
            tab.video_quality.show()
            tab.video_quality_label.show()
        self.resizeEvent(None)
        if self.current_table_index is not None:
            self.tab_models[self.current_table_index].manual_settings = tab.manual_settings.checkState() != 0
            self.state_service.save_tabs_state(self.tab_models)
        tab.remove_files_after_upload.setChecked(tab_model.remove_files_after_upload)

    def process(self, upload_after_download_form, upload_on, upload_time_type, upload_interval, new_media, upload_date, approve_download, current_table_index):
        table = self.tables[current_table_index]

        upload_in = None
        if upload_on:
            if upload_time_type == 0:
                upload_in = relativedelta(minutes=upload_interval)
            elif upload_time_type == 1:
                upload_in = relativedelta(hours=upload_interval)
            elif upload_time_type == 2:
                upload_in = relativedelta(days=upload_interval)
            else:
                upload_in = relativedelta(months=upload_interval)

        for i in range(0, table.rowCount()).__reversed__():

            if table.item(i, 3).checkState() == 0:
                continue

            upload_targets = list()
            channel = self.state_service.get_channel_by_url(self.tab_models[current_table_index].current_channel)
            hosting = Hosting[channel.hosting]
            title = None
            description = None
            upload_this = True
            try:
                video_info = hosting.value[0].get_video_info(table.item(i, 1).text(),
                                                             video_quality=self.tab_models[current_table_index].video_quality[1],
                                                             video_extension=self.tab_models[current_table_index].video_extension[1],
                                                             video_quality_str=self.tab_models[current_table_index].video_quality_str,
                                                             audio_quality_str=self.tab_models[current_table_index].audio_quality_str,
                                                             fps=self.tab_models[current_table_index].fps,
                                                             audio_bitrate=self.tab_models[current_table_index].audio_bitrate,
                                                             video_bitrate=self.tab_models[current_table_index].video_bitrate,
                                                             audio_sampling_rate=self.tab_models[current_table_index].audio_sampling_rate,
                                                             manual_settings=self.tab_models[current_table_index].manual_settings,
                                                             account=self.tab_models[current_table_index].account)

                title = video_info['title']
                if title is None:
                    title = ''
                if 'description' in video_info and description is None:
                    description = video_info['description']
                    if description is None:
                        description = ''

                # if self.tab_models[current_table_index].manual_settings and video_info['is_exists_format'][0] is False\
                #         and approve_download is False:
                #     agree_to_download_dialog = AgreeToDownloadDialog(None, video_info['is_exists_format'][1])
                #     agree_to_download_dialog.exec_()
                #
                #     if agree_to_download_dialog.is_agree is False:
                #         return
                #     else:
                #         approve_download = True
                #
                # if self.tab_models[current_table_index].manual_settings and self.state_service.if_video_has_been_loaded(table.item(i, 1).text(),
                #                                                self.tab_models[current_table_index].video_quality[1],
                #                                                self.tab_models[current_table_index].video_extension[1]):
                #     agree_to_repeat_download_dialog = AgreeToRepeatDownloadDialog(None)
                #     agree_to_repeat_download_dialog.exec_()
                #
                #     if agree_to_repeat_download_dialog.is_agree is False:
                #         continue

            except:
                log_error(traceback.format_exc())
                self.event_service.add_event(
                    Event(f'{get_str("technical_error")}: {table.item(i, 1).text()}'))
                upload_this = False
            video_size = None
            if upload_on and upload_this:
                video_size = video_info['filesize']
                # Если необходимо выгружать видео после загрузки, проводим валидацию
                for upload_target in upload_after_download_form.upload_targets:
                    upload_hosting = Hosting[upload_target['hosting']]
                    upload_target_copy = upload_target.copy()
                    upload_target_copy['id'] = uuid.uuid4()
                    try:
                        upload_target_copy['error'] = False
                        upload_hosting.value[0].validate_video_info_for_uploading(title=title,
                                                                                  description=description,
                                                                                  duration=video_info[
                                                                                      'duration'],
                                                                                  filesize=video_info[
                                                                                      'filesize'],
                                                                                  ext=video_info['ext'])

                    except VideoDurationException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_duration")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item('upload_yet',
                                                   upload_target_copy,
                                                   f'{get_str("bad_file_duration")}{video_info["title"]} {get_str("for_account")}'
                                                   f'{upload_hosting.name}, {upload_target["login"]}')
                        upload_target_copy['error'] = True
                    except FileSizeException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_size")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item('upload_yet',
                                                   upload_target_copy,
                                                   f'{get_str("bad_file_size")}{video_info["title"]} {get_str("for_account")}'
                                                   f'{upload_hosting.name}, {upload_target["login"]}')
                        upload_target_copy['error'] = True
                    except FileFormatException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_format")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item('upload_yet',
                                                   upload_target_copy,
                                                   f'{get_str("bad_file_format")}{video_info["title"]} {get_str("for_account")}'
                                                   f'{upload_hosting.name}, {upload_target["login"]}')
                        upload_target_copy['error'] = True
                    except NameIsTooLongException:
                        while (upload_hosting.value[0].title_size_restriction is not None and
                               len(title) > upload_hosting.value[0].title_size_restriction) or \
                                (upload_hosting.value[0].min_title_size is not None and
                                 len(title) < upload_hosting.value[0].min_title_size):
                            log_error(traceback.format_exc())
                            if upload_hosting.value[0].title_size_restriction is not None:
                                label = f'{get_str("bad_title")} ({str(upload_hosting.value[0].min_title_size)} <= {get_str("name")} > {str(upload_hosting.value[0].title_size_restriction)})'
                            else:
                                label = f'{get_str("bad_title")} ({str(upload_hosting.value[0].min_title_size)} <= {get_str("name")})'
                            form = TypeStrForm(parent=None,
                                               label=label,
                                               current_text=title)
                            form.exec_()
                            title = form.str
                    except DescriptionIsTooLongException:
                        while len(description) > upload_hosting.value[0].description_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=None,
                                               label=f'{get_str("too_long_description")}{str(upload_hosting.value[0].description_size_restriction)}',
                                               current_text=description)
                            form.exec_()
                            description = form.str
                    except Exception:
                        log_error(traceback.format_exc())
                        if StateService().get_settings().send_crash_notifications is True:
                            MailService().send_log()
                    upload_targets.append(upload_target_copy)

            queue_media = LoadQueuedMedia(media_id=str(uuid.uuid4()),
                                          url=table.item(i, 1).text(),
                                          account=self.tab_models[current_table_index].account,
                                          hosting=hosting.name,
                                          status=0,
                                          video_size=video_size,
                                          upload_after_download=upload_on and upload_this,
                                          upload_targets=upload_targets,
                                          upload_date=upload_date,
                                          upload_in=upload_in,
                                          format=self.tab_models[current_table_index].format[1],
                                          video_quality=self.tab_models[current_table_index].video_quality[1],
                                          video_extension=self.tab_models[current_table_index].video_extension[1],
                                          remove_files_after_upload=self.tab_models[current_table_index].remove_files_after_upload,
                                          title=title,
                                          description=description,
                                          download_dir=self.tab_models[current_table_index].download_dir,
                                          manual_settings=self.tab_models[current_table_index].manual_settings,
                                          video_quality_str=self.tab_models[current_table_index].video_quality_str,
                                          audio_quality_str=self.tab_models[current_table_index].audio_quality_str,
                                          audio_bitrate=self.tab_models[current_table_index].audio_bitrate,
                                          video_bitrate=self.tab_models[current_table_index].video_bitrate,
                                          fps=self.tab_models[current_table_index].fps,
                                          audio_sampling_rate=self.tab_models[current_table_index].audio_sampling_rate)
            upload_targets = list()

            # Если необходима выгрузка, учитывается интервал выгрузки, исходя из типа интервала. 1 видео выгружается сразу
            if upload_on and upload_this:

                for target in queue_media.upload_targets:
                    if target['error'] is False:
                        account = self.state_service.get_account_by_hosting_and_login(target['hosting'], target['login'])
                        self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(target['id']),
                                                                                          video_dir='upload_yet',
                                                                                          hosting=target['hosting'],
                                                                                          destination=target[
                                                                                              'upload_target'],
                                                                                          status=5,
                                                                                          account=account,
                                                                                          remove_files_after_upload=queue_media.remove_files_after_upload))

            new_media.append(queue_media)

        self.queue_media_service.add_to_the_download_queue(new_media)

    def on_add_media_to_query(self):

        table = self.tables[self.current_table_index]

        if table.rowCount() == 0:
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('need_load_video_list'))
            msg.exec_()
            return

        upload_after_download_form = None
        upload_on = False
        upload_time_type = None
        upload_interval = None
        upload_targets = None

        if self.tab_models[self.current_table_index].format[0] != 3:
            upload_after_download_form = UploadAfterDownloadForm(None)
            upload_after_download_form.exec_()

            if upload_after_download_form.passed == False:
                return

            upload_on = upload_after_download_form.upload_flag  # нужна ли выгрузка на хостинги после загрузки
            upload_time_type = upload_after_download_form.upload_interval_type  # тип интервала выгрузки после загрузки (мин, часы, дни, мес)
            upload_interval = upload_after_download_form.upload_interval  # сам интервал выгрузки после загрузки

        new_media = list()
        upload_date = datetime.datetime.now()
        approve_download = False

        thread = Thread(target=self.process, daemon=True, args=[upload_after_download_form, upload_on, upload_time_type, upload_interval, new_media, upload_date, approve_download, self.current_table_index])
        thread.start()

    def on_channel_changed(self, item):
        if item != '':
            if len(self.tab_models) != 0:
                self.tab_models[self.current_table_index].channel = item
                self.tab_models[self.current_table_index].hosting = self.state_service.get_channel_by_url(item).hosting
                self.state_service.save_tabs_state(self.tab_models)  # Каждый раз, когда меняются данные, они сохраняются

    def on_audio_bitrate_changed(self, item):
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].audio_bitrate = item
            self.state_service.save_tabs_state(self.tab_models)

    def on_video_bitrate_changed(self, item):
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].video_bitrate = item
            self.state_service.save_tabs_state(self.tab_models)

    def on_audio_sampling_rate_changed(self, item):
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].audio_sampling_rate = item
            self.state_service.save_tabs_state(self.tab_models)

    def on_fps_changed(self, item):
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].fps = item
            self.state_service.save_tabs_state(self.tab_models)

    def on_video_quality_changed(self, index):
        if self.first_start is False and len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].video_quality_str = index
            self.state_service.save_tabs_state(self.tab_models)

    def on_audio_quality_changed(self, index):
        if self.first_start is False and len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].audio_quality_str = index
            self.state_service.save_tabs_state(self.tab_models)

    def on_video_format_changed(self, item):
        format_list = list([None, 'NOT_MERGE', 'VIDEO', 'AUDIO'])
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].format = [item, format_list[item]]
            self.state_service.save_tabs_state(self.tab_models)  # Каждый раз, когда меняются данные, они сохраняются

    def on_video_resolution_changed(self, item):
        quality_list = list(['144', '240', '360', '480', '720', '1080', '1440', '2160'])
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].video_quality = [item, quality_list[item]]
            self.state_service.save_tabs_state(self.tab_models)

    def on_video_extension_changed(self, item):
        quality_list = list(['3gp', 'aac', 'flv', 'm4a', 'mp3', 'mp4', 'ogg', 'wav', 'webm'])
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].video_extension = [item, quality_list[item]]
            self.state_service.save_tabs_state(self.tab_models)

    def on_remove_files_after_upload_changed(self, item):
        if len(self.tab_models) != 0 and len(self.tab_models) > self.current_table_index:
            self.tab_models[self.current_table_index].remove_files_after_upload = item
            self.state_service.save_tabs_state(self.tab_models)

    def create_daemon_for_getting_video_list(self, button: AnimatedButton):
        button.start_animation()

        if self.tab_models[self.current_table_index].channel == None or self.tab_models[self.current_table_index].channel == '':
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('need_pick_some_channel'))
            msg.exec_()
            button.stop_animation()
            return list()

        # В существующем потоке выбираем аккаунт, если требуется, тк pyqt запрещает в других потоках
        # создавать формы используя parent widget из текущего потока
        channel = state_service.get_channel_by_url(self.tab_models[self.current_table_index].channel)
        hosting = Hosting[self.tab_models[self.current_table_index].hosting]
        account = None

        accounts = self.state_service.get_accounts_by_hosting(hosting.name)

        if len(accounts) == 0 and hosting.value[1]:
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('need_authorize'))
            msg.exec_()
            button.stop_animation()
            return list()
        elif len(accounts) != 0 and hosting.value[1]:
            choose_account_form = ChooseAccountForm(self, accounts)
            choose_account_form.exec_()

            if choose_account_form.account is None:
                button.stop_animation()
                return list()

            account = choose_account_form.account
        elif len(accounts) != 0:
            account = accounts[0]

        self.tab_models[self.current_table_index].account = account

        event_loop = None

        if hosting.value[0].is_async():
            event_loop = asyncio.new_event_loop()

        thread = Thread(target=self.get_video_list, daemon=True, args=[button, hosting, channel, account, event_loop, self.current_table_index])
        thread.start()

    def get_video_list(self, button: AnimatedButton, hosting, channel, account, event_loop, table_index):
        if channel is None:
            print()

        if event_loop is not None:
            asyncio.set_event_loop(event_loop)

        service = hosting.value[0]

        table = self.tables[table_index]

        while table.rowCount() > 0:
            table.removeRow(0)

        self.tab_models[table_index].video_list.clear()

        index = 0
        try:
            for video in service.get_videos_by_url(url=channel.url, account=account):
                table.insertRow(index)

                item1 = QtWidgets.QTableWidgetItem(video.name)
                item2 = QtWidgets.QTableWidgetItem(video.url)
                item3 = QtWidgets.QTableWidgetItem(video.date)
                item4 = QtWidgets.QTableWidgetItem()
                item4.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)
                item4.setCheckState(QtCore.Qt.Checked)

                video.checked = True

                is_downloaded = get_str('yes') \
                    if self.state_service.get_download_queue_media_by_url(video.url) is not None else get_str('no')

                item5 = QtWidgets.QTableWidgetItem(is_downloaded)

                table.setItem(index, 0, item1)
                table.setItem(index, 1, item2)
                table.setItem(index, 2, item3)
                table.setItem(index, 3, item4)
                table.setItem(index, 4, item5)

                self.tab_models[table_index].video_list.append(video)

                index += 1
        except:
            dialog = ShowErrorDialog(None, get_str('happened_error'), get_str('error'))
            dialog.exec_()
            log_error(traceback.format_exc())

        self.tab_models[table_index].current_channel = channel.url
        self.state_service.save_tabs_state(self.tab_models)

        table.update()
        button.stop_animation()

    def resizeEvent(self, event):
        self.change = False

        coef_x = self.parent().width() / 950
        coef_y = self.parent().height() / 600
        for tab in self.tabs:
            tab.choose_dir_button.setMaximumWidth(int(350 * coef_x))

            tab.channel_box.setGeometry(
                QtCore.QRect(int(20 * coef_x), int(40 * coef_y), int(590 * coef_x), int(30 * coef_y)))
            tab.add_button.setGeometry(
                QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(40 * coef_y), int(75 * coef_x), int(30 * coef_y))))
            tab.add_by_link_button.setGeometry(
                QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(80 * coef_y), int(300 * coef_x), int(30 * coef_y))))

            tab.manual_settings.setGeometry(
                QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(115 * coef_y), int(300 * coef_x), int(30 * coef_y))))
            tab.manual_settings_label.setGeometry(
                QtCore.QRect(QtCore.QRect(int(670 * coef_x), int(115 * coef_y), int(300 * coef_x), int(30 * coef_y))))

            if tab.manual_settings.checkState() != 0:
                tab.choose_video_quality_form.setGeometry(
                    QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(145 * coef_y), int(300 * coef_x), int(30 * coef_y))))
                tab.extension_chooser_combo_box.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(175 * coef_y), int(300 * coef_x), int(30 * coef_y)))
                tab.choose_video_format_combo_box.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(205 * coef_y), int(300 * coef_x), int(30 * coef_y)))
                tab.audio_bitrate.setGeometry(
                    QtCore.QRect(int(820 * coef_x), int(235 * coef_y), int(100 * coef_x), int(30 * coef_y)))
                tab.audio_bitrate_label.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(235 * coef_y), int(200 * coef_x), int(30 * coef_y)))
                tab.video_bitrate.setGeometry(
                    QtCore.QRect(int(820 * coef_x), int(265 * coef_y), int(100 * coef_x), int(30 * coef_y)))
                tab.video_bitrate_label.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(265 * coef_y), int(200 * coef_x), int(30 * coef_y)))
                tab.audio_sampling_rate.setGeometry(
                    QtCore.QRect(int(820 * coef_x), int(295 * coef_y), int(100 * coef_x), int(30 * coef_y)))
                tab.audio_sampling_rate_label.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(295 * coef_y), int(200 * coef_x), int(30 * coef_y)))
                tab.fps.setGeometry(
                    QtCore.QRect(int(820 * coef_x), int(325 * coef_y), int(100 * coef_x), int(30 * coef_y)))
                tab.fps_label.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(325 * coef_y), int(200 * coef_x), int(30 * coef_y)))
                tab.remove_files_after_upload_label.setGeometry(
                    QtCore.QRect(int(670 * coef_x), int(355 * coef_y), int(250 * coef_x), int(30 * coef_y)))
                tab.remove_files_after_upload.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(355 * coef_y), int(30 * coef_x), int(30 * coef_y)))
                tab.choose_dir_button.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(385 * coef_y), int(300 * coef_x), int(30 * coef_y)))
            else:
                tab.choose_video_format_combo_box.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(145 * coef_y), int(300 * coef_x), int(30 * coef_y)))
                tab.video_quality.setGeometry(
                    QtCore.QRect(int(820 * coef_x), int(175 * coef_y), int(100 * coef_x), int(30 * coef_y)))
                tab.video_quality_label.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(175 * coef_y), int(200 * coef_x), int(30 * coef_y)))
                tab.audio_quality.setGeometry(
                    QtCore.QRect(int(820 * coef_x), int(205 * coef_y), int(100 * coef_x), int(30 * coef_y)))
                tab.audio_quality_label.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(205 * coef_y), int(200 * coef_x), int(30 * coef_y)))
                tab.remove_files_after_upload_label.setGeometry(
                    QtCore.QRect(int(670 * coef_x), int(235 * coef_y), int(250 * coef_x), int(30 * coef_y)))
                tab.remove_files_after_upload.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(235 * coef_y), int(30 * coef_x), int(30 * coef_y)))
                tab.choose_dir_button.setGeometry(
                    QtCore.QRect(int(620 * coef_x), int(275 * coef_y), int(300 * coef_x), int(30 * coef_y)))

            tab.add_media_to_query_button.setGeometry(
                QtCore.QRect(int(700 * coef_x), int(40 * coef_y), int(150 * coef_x), int(30 * coef_y)))
            tab.table_widget.setGeometry(
                QtCore.QRect(int(20 * coef_x), int(80 * coef_y), int(590 * coef_x), int(420 * coef_y)))
            tab.reset_tab_settings_button.setGeometry(
                QtCore.QRect(int(620 * coef_x), int(470 * coef_y), int(300 * coef_x), int(30 * coef_y)))

            tab.table_widget.setColumnWidth(0, int(self.state_service.get_tab_column_weight(
                self.tabText(self.tabs.index(tab)), 0) * coef_x))
            tab.table_widget.setColumnWidth(1, int(self.state_service.get_tab_column_weight(
                self.tabText(self.tabs.index(tab)), 1) * coef_x))
            tab.table_widget.setColumnWidth(2, int(self.state_service.get_tab_column_weight(
                self.tabText(self.tabs.index(tab)), 2) * coef_x))
            tab.table_widget.setColumnWidth(3, int(self.state_service.get_tab_column_weight(
                self.tabText(self.tabs.index(tab)), 3) * coef_x))
            tab.table_widget.setColumnWidth(4, int(self.state_service.get_tab_column_weight(
                self.tabText(self.current_table_index), 4) * coef_x))

        self.change = True
        return super(LoadPageWidget, self).resizeEvent(event)

    def add_error_upload_item(self, video_link, target, error: str):
        self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(target['id']),
                                                                          video_dir=video_link,
                                                                          hosting=target['hosting'],
                                                                          status=6,
                                                                          account=self.state_service.get_account_by_hosting_and_login(
                                                                              target['hosting'],
                                                                              target['login']),
                                                                          destination=target[
                                                                              'upload_target'],
                                                                          upload_date=None,
                                                                          remove_files_after_upload=False,
                                                                          error_name=error))
