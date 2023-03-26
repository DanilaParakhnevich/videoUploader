from PyQt5 import QtCore, QtWidgets

from model.hosting import Hosting
from model.tab import TabModel
from service.state_service import StateService


class LoadPageWidget(QtWidgets.QTabWidget):

    _translate = QtCore.QCoreApplication.translate
    state_service = StateService()
    tabs = state_service.get_last_tabs()

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

        if len(self.tabs) == 0:
            self.createTab()
        else:
            for tab in self.tabs:
                self.create_tab(tab.tab_name, tab.channel, tab.hosting)

        self.setCurrentIndex(0)

    def remove_tab(self, index):
        self.tabs.pop(index - 1)
        self.widget(index)
        self.removeTab(index)

        self.state_service.save_tabs_state(self.tabs)

    def create_empty_tab(self):
        return self.create_tab(None, '', 0)

    def create_tab(self, name, link, selected):
        tab = QtWidgets.QWidget()
        tab.setObjectName("tab.py")
        videohosting_label = QtWidgets.QTextBrowser(tab)
        videohosting_label.setGeometry(QtCore.QRect(700, 0, 201, 31))
        videohosting_label.setObjectName("videohosting_label")

        combo_box = QtWidgets.QComboBox(tab)

        selected_index = 0

        for hosting in Hosting:
            combo_box.addItem(hosting.value)

            if selected == hosting.value:
                selected_index = combo_box.__len__() - 1

        combo_box.setCurrentIndex(selected_index)

        combo_box.setGeometry(QtCore.QRect(700, 30, 201, 30))
        combo_box.setObjectName("combo_box")

        link_label = QtWidgets.QTextBrowser(tab)
        link_label.setGeometry(QtCore.QRect(20, 10, 201, 31))
        link_label.setObjectName("link_label")
        link_edit = QtWidgets.QLineEdit(tab)
        link_edit.setGeometry(QtCore.QRect(20, 40, 591, 30))
        link_edit.setObjectName("link_edit")
        link_edit.setText(link)
        add_button = QtWidgets.QPushButton(tab)
        add_button.setGeometry(QtCore.QRect(620, 40, 51, 30))
        add_button.setObjectName("add_button")
        table_widget = QtWidgets.QTableWidget(tab)
        table_widget.setGeometry(QtCore.QRect(20, 80, 411, 421))
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

        self.insertTab(len(self.tabs), tab, "")

        videohosting_label.setHtml(self._translate("BuharVideoUploader",
                                              "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                              "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                              "p, li { white-space: pre-wrap; }\n"
                                              "</style></head><body style=\" font-family:\'Fira Sans Semi-Light\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Видеохостинг</p></body></html>"))
        link_label.setHtml(self._translate("BuharVideoUploader",
                                      "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                      "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                      "p, li { white-space: pre-wrap; }\n"
                                      "</style></head><body style=\" font-family:\'Fira Sans Semi-Light\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
                                      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ссылка</p></body></html>"))
        add_button.setText(self._translate("BuharVideoUploader", "Go"))
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
            index = len(self.tabs) + 1

            while True:
                val = True
                for i in range(len(self.tabs) + 1):
                    if self.tabText(i).endswith(f' {index}'):
                        index += 1
                        val = False
                        break
                if val:
                    break

            tab_name = self._translate("BuharVideoUploader", f'Tab {index}')
            self.setTabText(self.indexOf(tab), tab_name)

            self.tabs.append(TabModel(tab_name, '', Hosting.Youtube))
            self.state_service.save_tabs_state(self.tabs)

        combo_box.currentTextChanged.connect(self.on_hosting_changed)
        link_edit.textChanged.connect(self.on_url_changed)

    def on_hosting_changed(self, item):
        self.tabs[self.currentIndex() - 1].hosting = item
        self.state_service.save_tabs_state(self.tabs)

    def on_url_changed(self, item):
        self.tabs[self.currentIndex() - 1].channel = item
        self.state_service.save_tabs_state(self.tabs)

