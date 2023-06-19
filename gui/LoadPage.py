import asyncio
import datetime
import uuid

from dateutil.relativedelta import relativedelta

from PyQt5 import QtCore, QtWidgets

from gui.widgets.AddDownloadQueueViaLinkForm import AddDownloadQueueViaLinkForm
from gui.widgets.AgreeToDownloadDialog import AgreeToDownloadDialog
from gui.widgets.AgreeToRepeatDownloadDialog import AgreeToRepeatDownloadDialog
from gui.widgets.ChooseVideoQualityComboBox import ChooseVideoQualityComboBox
from gui.widgets.ExstensionChooserComboBox import ExtensionChooserComboBox
from gui.widgets.FormatChooserComboBox import FormatChooserComboBox
from gui.widgets.TypeStrForm import TypeStrForm
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
        if len(self.tab_models) == 0:
            self.create_empty_tab()
        else:
            for tab in self.tab_models:
                self.create_tab(tab.tab_name, tab.channel, tab.format[0], tab.video_quality[0], tab.video_extension[0],
                                tab.remove_files_after_upload, tab.download_dir if hasattr(tab, 'download_dir')
                                else self.state_service.get_settings().download_dir, tab.video_list)

        self.setCurrentIndex(0)
        self.event_service = EventService()

    def remove_tab(self, index):
        self.tab_models.pop(index - 1)
        self.tables.pop(index - 1)
        self.tabs.pop(index - 1)
        self.widget(index)
        self.removeTab(index)

        self.state_service.save_tabs_state(self.tab_models)

    def create_empty_tab(self):
        channels = self.state_service.get_channels()
        settings = self.state_service.get_settings()
        if len(channels) == 0:
            return self.create_tab(None, None, settings.format, settings.video_quality, settings.video_extension,
                                   settings.remove_files_after_upload, settings.download_dir)
        else:
            return self.create_tab(None, channels.__getitem__(0), settings.format, settings.video_quality,
                                   settings.video_extension, settings.remove_files_after_upload, settings.download_dir)

    # Этот метод добавляет новую вкладку, либо вкладку по известным данным из tab_models
    def create_tab(self, name, selected_channel, format_index, video_quality_index, video_extension,
                   remove_files_after_upload,
                   download_dir, video_list=list()):
        tab = QtWidgets.QWidget()
        tab.setObjectName("Tab.py")

        coef_x = self.parent().width() / 950
        coef_y = self.parent().height() / 600

        tab.channel_box = ChannelComboBox(tab, selected_channel)

        tab.channel_box.setGeometry(
            QtCore.QRect(int(20 * coef_x), int(40 * coef_y), int(590 * coef_x), int(30 * coef_y)))
        tab.channel_box.setObjectName("channel_box")
        tab.add_button = AnimatedButton(tab)
        tab.add_button.setGeometry(
            QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(40 * coef_y), int(75 * coef_x), int(30 * coef_y))))
        tab.add_button.setObjectName("add_button")
        tab.add_media_to_query_button = QtWidgets.QPushButton(tab)
        tab.add_media_to_query_button.setGeometry(
            QtCore.QRect(int(700 * coef_x), int(40 * coef_y), int(150 * coef_x), int(30 * coef_y)))
        tab.add_media_to_query_button.setObjectName('add_media_to_query_button')
        tab.add_by_link_button = AnimatedButton(tab)
        tab.add_by_link_button.setObjectName("add_button")
        tab.add_by_link_button.setGeometry(
            QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(100 * coef_y), int(300 * coef_x), int(30 * coef_y))))
        tab.add_by_link_button.setText(get_str('add_download_single_video_by_link'))
        tab.choose_video_format_combo_box = FormatChooserComboBox(tab)
        tab.choose_video_format_combo_box.setGeometry(QtCore.QRect(620, 150, 300, 30))
        tab.choose_video_format_combo_box.setObjectName('choose_video_format_combo_box')
        tab.choose_video_format_combo_box.setCurrentIndex(format_index)
        tab.choose_video_format_combo_box.currentIndexChanged.connect(self.on_video_format_changed)
        tab.choose_video_quality_form = ChooseVideoQualityComboBox(tab)
        tab.choose_video_quality_form.setGeometry(
            QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(200 * coef_y), int(300 * coef_x), int(30 * coef_y))))
        tab.choose_video_quality_form.setObjectName('choose_video_quality_form')
        tab.choose_video_quality_form.setCurrentIndex(video_quality_index)
        tab.choose_video_quality_form.currentIndexChanged.connect(self.on_video_quality_changed)
        tab.extension_chooser_combo_box = ExtensionChooserComboBox(tab)
        tab.extension_chooser_combo_box.setGeometry(
            QtCore.QRect(int(620 * coef_x), int(250 * coef_y), int(300 * coef_x), int(30 * coef_y)))
        tab.extension_chooser_combo_box.setObjectName('choose_video_quality_form')
        tab.extension_chooser_combo_box.setCurrentIndex(video_extension)
        tab.extension_chooser_combo_box.currentIndexChanged.connect(self.on_video_extension_changed)
        tab.choose_dir_button = QtWidgets.QPushButton(tab)
        tab.choose_dir_button.setObjectName("choose_dir_button")
        tab.choose_dir_button.setMaximumWidth(int(350 * coef_x))
        if download_dir == '..':
            tab.choose_dir_button.setText(get_str('choose_the_dir'))
        else:
            tab.choose_dir_button.setText(download_dir)

        def pick_new():
            dialog = QtWidgets.QFileDialog()
            folder_path = dialog.getExistingDirectory(None, get_str('choose_dir'))
            if folder_path != '':
                self.tab_models[self.currentIndex()].download_dir = folder_path
                self.state_service.save_tabs_state(self.tab_models)
                tab.choose_dir_button.setText(folder_path)

        tab.choose_dir_button.clicked.connect(pick_new)
        tab.choose_dir_button.setGeometry(
            QtCore.QRect(int(620 * coef_x), int(300 * coef_y), int(300 * coef_x), int(30 * coef_y)))
        tab.remove_files_after_upload = QtWidgets.QCheckBox(tab)
        tab.remove_files_after_upload.setGeometry(
            QtCore.QRect(int(620 * coef_x), int(350 * coef_y), int(30 * coef_x), int(30 * coef_y)))
        tab.remove_files_after_upload.setObjectName('remove_files_after_upload')
        tab.remove_files_after_upload.setChecked(remove_files_after_upload)
        tab.remove_files_after_upload.clicked.connect(self.on_remove_files_after_upload_changed)
        tab.remove_files_after_upload_label = QtWidgets.QLabel(tab)
        tab.remove_files_after_upload_label.setText(get_str('remove_files_after_upload'))
        tab.remove_files_after_upload_label.setGeometry(
            QtCore.QRect(int(670 * coef_x), int(350 * coef_y), int(250 * coef_x), int(30 * coef_y)))
        tab.remove_files_after_upload_label.setObjectName('remove_files_after_upload_label')

        tab.reset_tab_settings_button = QtWidgets.QPushButton(tab)
        tab.reset_tab_settings_button.setObjectName("reset_tab_settings_button")
        tab.reset_tab_settings_button.setText(get_str('reset_from_settings'))
        tab.reset_tab_settings_button.clicked.connect(self.reset_tab_settings)
        tab.reset_tab_settings_button.setGeometry(
            QtCore.QRect(int(620 * coef_x), int(450 * coef_y), int(300 * coef_x), int(30 * coef_y)))

        tab.choose_dir_button.clicked.connect(pick_new)
        tab.choose_dir_button.setGeometry(
            QtCore.QRect(int(620 * coef_x), int(300 * coef_y), int(300 * coef_x), int(30 * coef_y)))

        def on_add():
            form = AddDownloadQueueViaLinkForm(self, self.tab_models[self.current_table_index].format[0],
                                               self.tab_models[self.current_table_index].video_quality[1],
                                               self.tab_models[self.current_table_index].video_extension[1],
                                               self.tab_models[self.current_table_index].remove_files_after_upload)
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
                                              download_dir=tab.choose_dir_button.text())

                self.queue_media_service.add_to_the_download_queue(list([queue_media]))

        tab.add_by_link_button.clicked.connect(on_add)

        tab.table_widget = QtWidgets.QTableWidget(tab)
        tab.table_widget.setGeometry(
            QtCore.QRect(int(20 * coef_x), int(80 * coef_y), int(590 * coef_x), int(420 * coef_y)))
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
        index = 0

        for video in video_list:
            tab.table_widget.insertRow(index)

            item1 = QtWidgets.QTableWidgetItem(video.name)
            item2 = QtWidgets.QTableWidgetItem(video.url)
            item3 = QtWidgets.QTableWidgetItem(video.date)
            item4 = QtWidgets.QTableWidgetItem()
            item4.setFlags(QtCore.Qt.ItemIsUserCheckable |
                           QtCore.Qt.ItemIsEnabled)
            item4.setCheckState(QtCore.Qt.Checked)

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

        tab.table_widget.setColumnWidth(0, int(self.state_service.get_tab_column_weight(self.tabText(len(self.tabs)), 0) * coef_x))
        tab.table_widget.setColumnWidth(1, int(self.state_service.get_tab_column_weight(self.tabText(len(self.tabs)), 1) * coef_x))
        tab.table_widget.setColumnWidth(2, int(self.state_service.get_tab_column_weight(self.tabText(len(self.tabs)), 2) * coef_x))
        tab.table_widget.setColumnWidth(3, int(self.state_service.get_tab_column_weight(self.tabText(len(self.tabs)), 3) * coef_x))
        tab.table_widget.setColumnWidth(4, int(self.state_service.get_tab_column_weight(self.tabText(len(self.tabs)), 4) * coef_x))

        tab.add_media_to_query_button.clicked.connect(self.on_add_media_to_query)
        tab.channel_box.currentTextChanged.connect(self.on_channel_changed)
        self.tabs.append(tab)

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
        tab.remove_files_after_upload.setChecked(tab_model.remove_files_after_upload)
        tab.choose_dir_button.setText(tab_model.download_dir)

    def on_add_media_to_query(self):
        table = self.tables[self.currentIndex()]

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

        if self.tab_models[self.currentIndex()].format[0] != 3:
            upload_after_download_form = UploadAfterDownloadForm(self)
            upload_after_download_form.exec_()

            if upload_after_download_form.passed == False:
                return

            upload_on = upload_after_download_form.upload_flag  # нужна ли выгрузка на хостинги после загрузки
            upload_time_type = upload_after_download_form.upload_interval_type  # тип интервала выгрузки после загрузки (мин, часы, дни, мес)
            upload_interval = upload_after_download_form.upload_interval  # сам интервал выгрузки после загрузки
            upload_targets = list()  # выбранные канали для выгрузки

        new_media = list()
        upload_date = datetime.datetime.now()
        approve_download = False
        for i in range(0, table.rowCount()):

            if table.item(i, 3).checkState() == 0:
                continue

            channel = self.state_service.get_channel_by_url(self.tab_models[self.currentIndex()].channel)
            hosting = Hosting[channel.hosting]
            title = None
            description = None
            upload_this = True
            try:
                video_info = hosting.value[0].get_video_info(table.item(i, 1).text(),
                                                             self.tab_models[self.currentIndex()].video_quality[1],
                                                             self.tab_models[self.currentIndex()].video_extension[1],
                                                             self.tab_models[self.currentIndex()].account)
                title = video_info['title']
                if title is None:
                    title = ''
                if 'description' in video_info and description is None:
                    description = video_info['description']
                    if description is None:
                        description = ''

                if video_info['is_exists_format'][0] is False and approve_download is False:
                    agree_to_download_dialog = AgreeToDownloadDialog(self, video_info['is_exists_format'][1])
                    agree_to_download_dialog.exec_()

                    if agree_to_download_dialog.is_agree is False:
                        return
                    else:
                        approve_download = True

                if self.state_service.if_video_has_been_loaded(table.item(i, 1).text(),
                                                               self.tab_models[self.currentIndex()].video_quality[1],
                                                               self.tab_models[self.currentIndex()].video_extension[1]):
                    agree_to_repeat_download_dialog = AgreeToRepeatDownloadDialog(self)
                    agree_to_repeat_download_dialog.exec_()

                    if agree_to_repeat_download_dialog.is_agree is False:
                        continue

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
                    try:
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
                        self.add_error_upload_item(table.item(i, 1).text(),
                                                   upload_target,
                                                   f'{get_str("bad_file_duration")}{video_info["title"]} {get_str("for_account")}'
                                                   f'{upload_hosting.name}, {upload_target["login"]}')
                        continue
                    except FileSizeException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_size")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item(table.item(i, 1).text(),
                                                   upload_target,
                                                   f'{get_str("bad_file_size")}{video_info["title"]} {get_str("for_account")}'
                                                   f'{upload_hosting.name}, {upload_target["login"]}')
                        continue
                    except FileFormatException:
                        log_error(traceback.format_exc())
                        self.event_service.add_event(
                            Event(f'{get_str("bad_file_format")}{video_info["title"]} {get_str("for_account")}'
                                  f'{upload_hosting.name}, {upload_target["login"]}'))
                        self.add_error_upload_item(table.item(i, 1).text(),
                                                   upload_target,
                                                   f'{get_str("bad_file_format")}{video_info["title"]} {get_str("for_account")}'
                                                   f'{upload_hosting.name}, {upload_target["login"]}')
                        continue
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
                            form = TypeStrForm(parent=self,
                                               label=label,
                                               current_text=title)
                            form.exec_()
                            title = form.str
                    except DescriptionIsTooLongException:
                        while len(description) > upload_hosting.value[0].description_size_restriction:
                            log_error(traceback.format_exc())
                            form = TypeStrForm(parent=self,
                                               label=f'{get_str("too_long_description")}{str(upload_hosting.value[0].description_size_restriction)}',
                                               current_text=description)
                            form.exec_()
                            description = form.str
                    except Exception:
                        log_error(traceback.format_exc())
                        if StateService().get_settings().send_crash_notifications is True:
                            MailService().send_log()

                    upload_targets.append(upload_target)

            queue_media = LoadQueuedMedia(media_id=str(uuid.uuid4()),
                                          url=table.item(i, 1).text(),
                                          account=self.tab_models[self.currentIndex()].account,
                                          hosting=hosting.name,
                                          status=0,
                                          video_size=video_size,
                                          upload_after_download=upload_on and upload_this,
                                          upload_targets=upload_targets,
                                          upload_date=upload_date,
                                          format=self.tab_models[self.currentIndex()].format[1],
                                          video_quality=self.tab_models[self.currentIndex()].video_quality[1],
                                          video_extension=self.tab_models[self.currentIndex()].video_extension[1],
                                          remove_files_after_upload=self.tab_models[
                                              self.currentIndex()].remove_files_after_upload,
                                          title=title,
                                          description=description,
                                          download_dir=self.tab_models[
                                              self.currentIndex()].download_dir)
            upload_targets = list()

            # Если необходима выгрузка, учитывается интервал выгрузки, исходя из типа интервала. 1 видео выгружается сразу
            if upload_on:
                if upload_time_type == 0:
                    upload_date = upload_date + relativedelta(minutes=upload_interval)
                elif upload_time_type == 1:
                    upload_date = upload_date + relativedelta(hours=upload_interval)
                elif upload_time_type == 2:
                    upload_date = upload_date + relativedelta(days=upload_interval)
                else:
                    upload_date = upload_date + relativedelta(months=upload_interval)

                for target in queue_media.upload_targets:
                    account = self.state_service.get_account_by_hosting_and_login(target['hosting'], target['login'])
                    self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(uuid.uuid4()),
                                                                                      video_dir=get_str('upload_yet'),
                                                                                      hosting=target['hosting'],
                                                                                      destination=target[
                                                                                          'upload_target'],
                                                                                      status=5,
                                                                                      account=account,
                                                                                      remove_files_after_upload=queue_media.remove_files_after_upload))

            new_media.append(queue_media)

        self.queue_media_service.add_to_the_download_queue(new_media)

    def on_channel_changed(self, item):
        if item != '':
            self.tab_models[self.currentIndex()].channel = item
            self.tab_models[self.currentIndex()].hosting = self.state_service.get_channel_by_url(item).hosting
            self.state_service.save_tabs_state(self.tab_models)  # Каждый раз, когда меняются данные, они сохраняются

    def on_video_format_changed(self, item):
        format_list = list([None, 'NOT_MERGE', 'VIDEO', 'AUDIO'])
        self.tab_models[self.currentIndex()].format = [item, format_list[item]]
        self.state_service.save_tabs_state(self.tab_models)  # Каждый раз, когда меняются данные, они сохраняются

    def on_video_quality_changed(self, item):
        quality_list = list(['144', '240', '360', '480', '720', '1080', '1440', '2160'])
        self.tab_models[self.currentIndex()].video_quality = [item, quality_list[item]]
        self.state_service.save_tabs_state(self.tab_models)

    def on_video_extension_changed(self, item):
        quality_list = list(['3gp', 'aac', 'flv', 'm4a', 'mp3', 'mp4', 'ogg', 'wav', 'webm'])
        self.tab_models[self.currentIndex()].video_extension = [item, quality_list[item]]
        self.state_service.save_tabs_state(self.tab_models)

    def on_remove_files_after_upload_changed(self, item):
        self.tab_models[self.currentIndex()].remove_files_after_upload = item
        self.state_service.save_tabs_state(self.tab_models)

    def create_daemon_for_getting_video_list(self, button: AnimatedButton):
        button.start_animation()

        if self.tab_models[self.currentIndex()].channel == None or self.tab_models[self.currentIndex()].channel == '':
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('need_pick_some_channel'))
            msg.exec_()
            button.stop_animation()
            return list()

        # В существующем потоке выбираем аккаунт, если требуется, тк pyqt запрещает в других потоках
        # создавать формы используя parent widget из текущего потока
        channel = state_service.get_channel_by_url(self.tab_models[self.currentIndex()].channel)
        hosting = Hosting[self.tab_models[self.currentIndex()].hosting]
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

        self.tab_models[self.currentIndex()].account = account

        event_loop = None

        if hosting.value[0].is_async():
            event_loop = asyncio.new_event_loop()

        thread = Thread(target=self.get_video_list, daemon=True, args=[button, hosting, channel, account, event_loop])
        thread.start()

    def get_video_list(self, button: AnimatedButton, hosting, channel, account, event_loop):
        if channel is None:
            print()

        if event_loop is not None:
            asyncio.set_event_loop(event_loop)

        service = hosting.value[0]

        table = self.tables[self.currentIndex()]

        while table.rowCount() > 0:
            table.removeRow(0)

        self.tab_models[self.currentIndex()].video_list.clear()

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

                is_downloaded = get_str('yes') \
                    if self.state_service.get_download_queue_media_by_url(video.url) is not None else get_str('no')

                item5 = QtWidgets.QTableWidgetItem(is_downloaded)

                table.setItem(index, 0, item1)
                table.setItem(index, 1, item2)
                table.setItem(index, 2, item3)
                table.setItem(index, 3, item4)
                table.setItem(index, 4, item5)

                self.tab_models[self.currentIndex()].video_list.append(video)

                index += 1
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('happened_error'))
            msg.exec_()
            log_error(traceback.format_exc())

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
                QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(100 * coef_y), int(300 * coef_x), int(30 * coef_y))))
            tab.choose_video_quality_form.setGeometry(
                QtCore.QRect(QtCore.QRect(int(620 * coef_x), int(200 * coef_y), int(300 * coef_x), int(30 * coef_y))))
            tab.extension_chooser_combo_box.setGeometry(
                QtCore.QRect(int(620 * coef_x), int(250 * coef_y), int(300 * coef_x), int(30 * coef_y)))
            tab.remove_files_after_upload_label.setGeometry(
                QtCore.QRect(int(670 * coef_x), int(350 * coef_y), int(250 * coef_x), int(30 * coef_y)))
            tab.remove_files_after_upload.setGeometry(
                QtCore.QRect(int(620 * coef_x), int(350 * coef_y), int(30 * coef_x), int(30 * coef_y)))
            tab.choose_dir_button.setGeometry(
                QtCore.QRect(int(620 * coef_x), int(300 * coef_y), int(300 * coef_x), int(30 * coef_y)))
            tab.choose_video_format_combo_box.setGeometry(
                QtCore.QRect(int(620 * coef_x), int(150 * coef_y), int(300 * coef_x), int(30 * coef_y)))
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
        self.queue_media_service.add_to_the_upload_queue(UploadQueueMedia(media_id=str(uuid.uuid4()),
                                                                          video_dir=video_link,
                                                                          hosting=target['hosting'],
                                                                          status=3,
                                                                          account=self.state_service.get_account_by_hosting_and_login(
                                                                              target['hosting'],
                                                                              target['login']),
                                                                          destination=target[
                                                                              'upload_target'],
                                                                          upload_date=None,
                                                                          remove_files_after_upload=False,
                                                                          error_name=error))
