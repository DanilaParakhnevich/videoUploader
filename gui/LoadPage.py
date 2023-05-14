import asyncio
import datetime
from dateutil.relativedelta import relativedelta

from PyQt5 import QtCore, QtWidgets

from gui.widgets.ChooseHostingForm import ChooseHostingForm
from gui.widgets.ChooseVideoQualityComboBox import ChooseVideoQualityComboBox
from gui.widgets.FormatChooserComboBox import FormatChooserComboBox
from gui.widgets.TypeStrForm import TypeStrForm
from model.LoadQueuedMedia import LoadQueuedMedia
from model.Hosting import Hosting
from model.Tab import TabModel
from gui.widgets.ChannelComboBox import ChannelComboBox
from gui.widgets.ChooseAccountForm import ChooseAccountForm
from gui.widgets.UploadAfterDownloadForm import UploadAfterDownloadForm
from gui.widgets.LoadingButton import AnimatedButton
from gui.widgets.ChooseChannelForm import ChooseChannelForm
from service.LocalizationService import *
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

        if len(self.tab_models) == 0:
            self.create_empty_tab()
        else:
            for tab in self.tab_models:
                self.create_tab(tab.tab_name, tab.channel, tab.format[0], tab.video_quality[0],
                                tab.remove_files_after_upload)

        self.setCurrentIndex(0)

    def remove_tab(self, index):
        self.tab_models.pop(index - 1)
        self.tables.pop(index - 1)
        self.widget(index)
        self.removeTab(index)

        self.state_service.save_tabs_state(self.tab_models)

    def create_empty_tab(self):
        channels = self.state_service.get_channels()
        if len(channels) == 0:
            return self.create_tab(None, None, 0, 0, 0)
        else:
            return self.create_tab(None, channels.__getitem__(0), 0, 0, 0)

    # Этот метод добавляет новую вкладку, либо вкладку по известным данным из tab_models
    def create_tab(self, name, selected_channel, format_index, video_quality_index, remove_files_after_upload):
        tab = QtWidgets.QWidget()
        tab.setObjectName("Tab.py")

        tab.channel_box = ChannelComboBox(tab, selected_channel)

        tab.channel_box.setGeometry(QtCore.QRect(20, 40, 591, 30))
        tab.channel_box.setObjectName("channel_box")
        add_button = AnimatedButton(tab)
        add_button.setGeometry(QtCore.QRect(620, 40, 75, 30))
        add_button.setObjectName("add_button")
        add_media_to_query_button = QtWidgets.QPushButton(tab)
        add_media_to_query_button.setGeometry(QtCore.QRect(700, 40, 150, 30))
        add_media_to_query_button.setObjectName('add_media_to_query_button')
        tab.choose_video_format_combo_box = FormatChooserComboBox(tab)
        tab.choose_video_format_combo_box.setGeometry(QtCore.QRect(620, 100, 300, 30))
        tab.choose_video_format_combo_box.setObjectName('choose_video_format_combo_box')
        tab.choose_video_format_combo_box.setCurrentIndex(format_index)
        tab.choose_video_format_combo_box.currentIndexChanged.connect(self.on_video_format_changed)
        tab.choose_video_quality_form = ChooseVideoQualityComboBox(tab)
        tab.choose_video_quality_form.setGeometry(QtCore.QRect(620, 150, 300, 30))
        tab.choose_video_quality_form.setObjectName('choose_video_quality_form')
        tab.choose_video_quality_form.setCurrentIndex(video_quality_index)
        tab.choose_video_quality_form.currentIndexChanged.connect(self.on_video_quality_changed)
        tab.remove_files_after_upload = QtWidgets.QCheckBox(tab)
        tab.remove_files_after_upload.setGeometry(QtCore.QRect(620, 200, 30, 30))
        tab.remove_files_after_upload.setObjectName('remove_files_after_upload')
        tab.remove_files_after_upload.setChecked(remove_files_after_upload)
        tab.remove_files_after_upload.clicked.connect(self.on_remove_files_after_upload_changed)
        remove_files_after_upload_label = QtWidgets.QLabel(tab)
        remove_files_after_upload_label.setText(get_str('remove_files_after_upload'))
        remove_files_after_upload_label.setGeometry(QtCore.QRect(670, 200, 250, 30))
        remove_files_after_upload_label.setObjectName('remove_files_after_upload_label')
        table_widget = QtWidgets.QTableWidget(tab)
        table_widget.setGeometry(QtCore.QRect(20, 80, 500, 421))
        table_widget.setObjectName("table_widget")
        table_widget.setColumnCount(5)
        table_widget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(4, item)

        self.insertTab(len(self.tables), tab, "")

        add_button.setText(get_str('get'))
        add_button.clicked.connect(lambda: self.create_daemon_for_getting_video_list(add_button))
        add_media_to_query_button.setObjectName("download_button")
        add_media_to_query_button.setText(get_str('add_to_the_queue'))
        item = table_widget.horizontalHeaderItem(0)
        item.setText(get_str("name"))
        item = table_widget.horizontalHeaderItem(1)
        item.setText(get_str("link"))
        item = table_widget.horizontalHeaderItem(2)
        item.setText(get_str("date"))
        item = table_widget.horizontalHeaderItem(3)
        item.setText(get_str("is_download"))
        item = table_widget.horizontalHeaderItem(4)
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

            self.tab_models.append(TabModel(tab_name, '', Hosting.Youtube.name, [0, None], [0, '144'], False))
            self.state_service.save_tabs_state(self.tab_models)
        self.tables.append(table_widget)

        add_media_to_query_button.clicked.connect(self.on_add_media_to_query)
        tab.channel_box.currentTextChanged.connect(self.on_channel_changed)

    def on_add_media_to_query(self):
        table = self.tables[self.currentIndex()]

        if table.rowCount() == 0:
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('need_load_video_list'))
            msg.exec_()
            return

        upload_on = False
        upload_time_type = None
        upload_interval = None
        upload_hosting = None
        upload_account = None
        upload_target = None

        if self.tab_models[self.currentIndex()].format[0] != 3:
            upload_after_download_form = UploadAfterDownloadForm(self)
            upload_after_download_form.exec_()

            if upload_after_download_form.passed == False:
                return

            upload_on = upload_after_download_form.upload_flag  # нужна ли выгрузка на хостинги после загрузки
            upload_time_type = upload_after_download_form.upload_interval_type  # тип интервала выгрузки после загрузки (мин, часы, дни, мес)
            upload_interval = upload_after_download_form.upload_interval  # сам интервал выгрузки после загрузки
            upload_hosting = upload_after_download_form.upload_hosting
            upload_target = upload_after_download_form.upload_target
            upload_account = upload_after_download_form.upload_account

        current_media_query = self.state_service.get_download_queue_media()

        new_media = list()
        upload_date = datetime.datetime.now()
        for i in range(0, table.rowCount()):

            if table.item(i, 3).checkState() == 0:
                continue

            is_exist = False

            for media in current_media_query:
                if media.url == table.item(i, 1).text():
                    log_info(get_str('media_already_in_the_queue').format(media.url))
                    is_exist = True
                    break

            if is_exist:
                continue

            title = None
            description = None
            channel = self.state_service.get_channel_by_url(self.tab_models[self.currentIndex()].channel)
            hosting = Hosting[channel.hosting]

            if upload_on:
                video_info = hosting.value[0].get_video_info(table.item(i, 1).text(),
                                                             self.tab_models[
                                                                 self.currentIndex()].video_quality[1],
                                                             self.tab_models[self.currentIndex()].account)
                try:
                    upload_hosting.value[0].validate_video_info_for_uploading(title=video_info['title'],
                                                                              description=video_info[
                                                                                  'description'],
                                                                              duration=video_info[
                                                                                  'duration'],
                                                                              filesize=video_info[
                                                                                  'filesize'],
                                                                              ext=video_info['ext'])
                except VideoDurationException:
                    log_error(traceback.format_exc())
                    msg = QtWidgets.QMessageBox()
                    msg.setText(f'{get_str("bad_file_duration")}{video_info["title"]}')
                    msg.exec_()
                    upload_on = False
                except FileSizeException:
                    log_error(traceback.format_exc())
                    msg = QtWidgets.QMessageBox()
                    msg.setText(f'{get_str("bad_file_size")}{video_info["title"]}')
                    msg.exec_()
                    upload_on = False
                except FileFormatException:
                    log_error(traceback.format_exc())
                    msg = QtWidgets.QMessageBox()
                    msg.setText(f'{get_str("bad_file_format")}{video_info["title"]}')
                    msg.exec_()
                    upload_on = False
                except NameIsTooLongException:
                    title = video_info['title']
                    while len(title) > upload_hosting.value[0].title_size_restriction:
                        log_error(traceback.format_exc())
                        form = TypeStrForm(parent=self,
                                           label=f'{get_str("too_long_title")}{str(upload_hosting.value[0].title_size_restriction)}',
                                           current_text=title)
                        form.exec_()
                        title = form.str

                except DescriptionIsTooLongException:
                    description = video_info['description']
                    while len(description) > upload_hosting.value[0].description_size_restriction:
                        log_error(traceback.format_exc())
                        form = TypeStrForm(parent=self,
                                           label=f'{get_str("too_long_description")}{str(upload_hosting.value[0].description_size_restriction)}',
                                           current_text=description)
                        form.exec_()
                        description = form.str

            queue_media = LoadQueuedMedia(url=table.item(i, 1).text(),
                                          account=self.tab_models[self.currentIndex()].account,
                                          hosting=hosting.name,
                                          status=0,
                                          upload_after_download=upload_on,
                                          upload_destination=upload_target,
                                          upload_date=upload_date,
                                          upload_account=upload_account,
                                          format=self.tab_models[self.currentIndex()].format[1],
                                          video_quality=self.tab_models[self.currentIndex()].video_quality[1],
                                          remove_files_after_upload=self.tab_models[
                                              self.currentIndex()].remove_files_after_upload,
                                          title=title,
                                          description=description)

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
        elif len(accounts) == 1:
            account = accounts[0]
        elif len(accounts) > 1:
            self.form = ChooseAccountForm(parent=self.parentWidget(), accounts=accounts)
            self.form.exec()
            account = self.form.account

        self.tab_models[self.currentIndex()].account = account

        event_loop = None

        if hosting.value[0].is_async():
            event_loop = asyncio.new_event_loop()

        thread = Thread(target=self.get_video_list, daemon=True, args=[button, hosting, channel, account, event_loop])
        thread.start()

    def get_video_list(self, button: AnimatedButton, hosting, channel, account, event_loop):
        if event_loop is not None:
            asyncio.set_event_loop(event_loop)

        service = hosting.value[0]

        table = self.tables[self.currentIndex()]

        while table.rowCount() > 0:
            table.removeRow(0)

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

                index += 1
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText(get_str('happened_error'))
            msg.exec_()
            log_error(traceback.format_exc())

        button.stop_animation()
