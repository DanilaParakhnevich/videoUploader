from PyQt5 import QtCore, QtWidgets
from widgets.ChooseAccountForm import ChooseAccountForm

from model.LoadQueuedMedia import LoadQueuedMedia
from model.Hosting import Hosting
from model.Tab import TabModel
from gui.widgets.ChannelComboBox import ChannelComboBox
from gui.widgets.SpecialSourceForm import SpecialSourceForm
from service.StateService import StateService
from service.QueueMediaService import QueueMediaService
from threading import Thread
from service.LoggingService import *
import asyncio


class LoadPageWidget(QtWidgets.QTabWidget):

    _translate = QtCore.QCoreApplication.translate
    state_service = StateService()
    queue_media_service = QueueMediaService()
    tab_models = state_service.get_last_tabs()
    tables = list()

    def __init__(self, central_widget):

        super(LoadPageWidget, self).__init__(central_widget)

        self.setObjectName("tab_widget")

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
                self.create_tab(tab.tab_name, tab.channel)

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
            return self.create_tab(None, None)
        else:
            return self.create_tab(None, channels.__getitem__(0))

    def create_tab(self, name, selected_channel):
        tab = QtWidgets.QWidget()
        tab.setObjectName("Tab.py")

        tab.channel_box = ChannelComboBox(tab, selected_channel)

        tab.channel_box.setGeometry(QtCore.QRect(20, 40, 591, 30))
        tab.channel_box.setObjectName("link_edit")
        add_button = QtWidgets.QPushButton(tab)
        add_button.setGeometry(QtCore.QRect(620, 40, 51, 30))
        add_button.setObjectName("add_button")
        add_media_to_query_button = QtWidgets.QPushButton(tab)
        add_media_to_query_button.setGeometry(QtCore.QRect(680, 40, 100, 30))
        add_media_to_query_button.setObjectName('add_media_to_query_button')
        table_widget = QtWidgets.QTableWidget(tab)
        table_widget.setGeometry(QtCore.QRect(20, 80, 500, 421))
        table_widget.setObjectName("table_widget")
        table_widget.setColumnCount(4)
        table_widget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        table_widget.setHorizontalHeaderItem(3, item)

        self.insertTab(len(self.tables), tab, "")

        add_button.setText(self._translate("BuharVideoUploader", "Go"))
        add_button.clicked.connect(self.create_daemon_for_getting_video_list)
        add_media_to_query_button.setObjectName("download_button")
        add_media_to_query_button.setText(self._translate("BuharVideoUploader", "Add to queue"))
        item = table_widget.horizontalHeaderItem(0)
        item.setText(self._translate("BuharVideoUploader", "Название"))
        item = table_widget.horizontalHeaderItem(1)
        item.setText(self._translate("BuharVideoUploader", "Ссылка"))
        item = table_widget.horizontalHeaderItem(2)
        item.setText(self._translate("BuharVideoUploader", "Дата"))
        item = table_widget.horizontalHeaderItem(3)
        item.setText(self._translate("BuharVideoUploader", "Качать?"))

        if name:
            self.setTabText(self.indexOf(tab), name)
        else:
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

            tab_name = self._translate("BuharVideoUploader", f'Tab {index}')
            self.setTabText(self.indexOf(tab), tab_name)

            self.tab_models.append(TabModel(tab_name, '', Hosting.Youtube.name))
            self.state_service.save_tabs_state(self.tab_models)
        self.tables.append(table_widget)

        add_media_to_query_button.clicked.connect(self.on_add_media_to_query)
        tab.channel_box.currentTextChanged.connect(self.on_channel_changed)

    def on_add_media_to_query(self):
        table = self.tables[self.currentIndex()]

        if table.rowCount() == 0:
            msg = QtWidgets.QMessageBox()
            msg.setText('Необходимо подгрузить видео с канала')
            msg.exec_()
            return

        upload_on = True

        current_media_query = self.state_service.get_download_queue_media()

        service = Hosting[self.hosting].value[0]

        source = None

        if service.need_to_be_uploaded_to_special_source():
            sourceForm = SpecialSourceForm(self, self.hosting, service, self.account)
            sourceForm.exec_()

            if sourceForm.passed:
                source = sourceForm.source_edit.text()
            else:
                return

        new_media = list()
        for i in range(0, table.rowCount()):

            if table.item(i, 3).checkState() == 0:
                continue

            self.channel = self.state_service.get_channel_by_url(self.tab_models[self.currentIndex()].channel)
            self.hosting = self.channel.hosting

            is_exist = False

            for media in current_media_query:
                if media.url == table.item(i, 1).text():
                    log_info(f'Медиа "{media.url}" уже в списке очереди')
                    is_exist = True
                    break

            if is_exist:
                continue

            queue_media = LoadQueuedMedia(url=table.item(i, 1).text(),
                                          account=self.account,
                                          hosting=self.hosting,
                                          status=0,
                                          upload_after_download=upload_on,
                                          upload_destination=source)

            new_media.append(queue_media)

        self.queue_media_service.add_to_the_download_queue(new_media)

    def on_channel_changed(self, item):
        self.tab_models[self.currentIndex()].channel = item
        self.state_service.save_tabs_state(self.tab_models)

    def create_daemon_for_getting_video_list(self):

        # В существующем потоке выбираем аккаунт, если требуется, тк pyqt запрещает в других потоках
        # создавать формы используя parent widget из текущего потока
        self.channel = self.state_service.get_channel_by_url(self.tab_models[self.currentIndex()].channel)
        self.hosting = Hosting[self.channel.hosting]
        self.account = None

        accounts = self.state_service.get_accounts_by_hosting(self.hosting.name)

        if len(accounts) == 0 and self.hosting.value[1]:
            msg = QtWidgets.QMessageBox()
            msg.setText('Необходимо авторизоваться на странице "Аккаунты"')
            msg.exec_()
            return list()
        elif len(accounts) == 1:
            self.account = accounts[0]
        elif len(accounts) > 1:
            self.form = ChooseAccountForm(parent=self.parentWidget(), accounts=accounts)
            self.form.exec()
            self.account = self.form.account

        thread = Thread(target=self.get_video_list, daemon=True, args=[asyncio.get_event_loop()])
        thread.start()

    def get_video_list(self, event_loop):
        asyncio.set_event_loop(event_loop)
        service = self.hosting.value[0]

        table = self.tables[self.currentIndex()]

        while table.rowCount() > 0:
            table.removeRow(0)

        index = 0
        try:
            for video in service.get_videos_by_url(url=self.channel.url, account=self.account):
                table.insertRow(index)

                item1 = QtWidgets.QTableWidgetItem(video.name)
                item2 = QtWidgets.QTableWidgetItem(video.url)
                item3 = QtWidgets.QTableWidgetItem(video.date)
                item4 = QtWidgets.QTableWidgetItem()
                item4.setFlags(QtCore.Qt.ItemIsUserCheckable |
                              QtCore.Qt.ItemIsEnabled)
                item4.setCheckState(QtCore.Qt.Checked)

                table.setItem(index, 0, item1)
                table.setItem(index, 1, item2)
                table.setItem(index, 2, item3)
                table.setItem(index, 3, item4)

                index += 1
        except:
            msg = QtWidgets.QMessageBox()
            msg.setText('Произошла ошибка')
            msg.exec_()
            log_error(traceback.format_exc())
