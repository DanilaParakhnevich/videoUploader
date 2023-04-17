from PyQt5 import QtCore, QtWidgets

from model.hosting import Hosting
from service.StateService import StateService
from model.channel import Channel


class ChannelsPageWidget(QtWidgets.QTableWidget):
    comboBox = QtWidgets.QComboBox()
    url_edit = QtWidgets.QLineEdit()

    state_service = StateService()

    channels = state_service.get_channels()

    def __init__(self, central_widget):
        super(ChannelsPageWidget, self).__init__(central_widget)
        self.setMinimumSize(QtCore.QSize(0, 440))
        self.setObjectName("accounts_page_widget")
        self.setColumnCount(3)
        self.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(2, item)
        self.horizontalHeader().setDefaultSectionSize(310)

        horizontal_layout = QtWidgets.QHBoxLayout(self)
        horizontal_layout.setObjectName("horizontal_layout")

        self.comboBox.setParent(central_widget)
        for hosting in Hosting:
            self.comboBox.addItem(hosting.name)
        self.comboBox.setMaximumWidth(50)
        self.comboBox.setObjectName("comboBox")

        horizontal_layout.addWidget(self.comboBox)
        self.url_edit.setParent(central_widget)
        self.url_edit.setObjectName("url_edit")
        horizontal_layout.addWidget(self.url_edit)
        add_button = QtWidgets.QPushButton(central_widget)
        add_button.setObjectName("add_button")
        horizontal_layout.addWidget(add_button)

        add_button.clicked.connect(self.on_add)

        _translate = QtCore.QCoreApplication.translate
        item = self.horizontalHeaderItem(0)
        item.setText(_translate("BuharVideoUploader", "Видеохостинг"))
        item = self.horizontalHeaderItem(1)
        item.setText(_translate("BuharVideoUploader", "Ссылка"))
        item = self.horizontalHeaderItem(2)
        item.setText(_translate("BuharVideoUploader", "Удалить"))
        add_button.setText(_translate("BuharVideoUploader", "Добавить"))

        self.url_edit.setPlaceholderText(_translate("BuharVideoUploader", "Ссылка на канал"))

        for channel in self.channels:
            self.insertRow(self.rowCount())
            item1 = QtWidgets.QTableWidgetItem(channel.hosting)
            item2 = QtWidgets.QTableWidgetItem(channel.url)

            input_position = self.rowCount() - 1

            btn = QtWidgets.QPushButton(self)
            btn.setText('-')
            self.setCellWidget(input_position, 2, btn)

            btn.clicked.connect(self.on_delete_row)

            self.setItem(input_position, 0, item1)
            self.setItem(input_position, 1, item2)

    def on_add(self):
        hosting = Hosting[self.comboBox.currentText()]

        # Если для работы с хостингом необходима авторизация:
        try:
            if hosting.value[1]:
                hosting.value[0].show_login_dialog(hosting, self.url_edit.text(), self.parentWidget())
            else:
                self.channels.append(Channel(hosting=self.comboBox.currentText(), url=self.url_edit.text()))
                self.state_service.save_channels(self.channels)
        except:
            return

        self.insertRow(self.rowCount())
        item1 = QtWidgets.QTableWidgetItem(self.comboBox.currentText())
        item2 = QtWidgets.QTableWidgetItem(self.url_edit.text())

        input_position = self.rowCount() - 1

        btn = QtWidgets.QPushButton(self)
        btn.setText('-')
        self.setCellWidget(input_position, 2, btn)

        btn.clicked.connect(self.on_delete_row)

        self.setItem(input_position, 0, item1)
        self.setItem(input_position, 1, item2)

        self.url_edit.setText('')

    def on_delete_row(self):
        button = self.sender()
        if button:
            row = self.indexAt(button.pos()).row()
            self.removeRow(row)
            self.channels.pop(row)
            self.state_service.save_channels(self.channels)
