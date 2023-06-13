from PyQt5 import QtCore, QtWidgets

from model.Hosting import Hosting
from model.Channel import Channel
from service.LocalizationService import *
from logging import *


class ChannelsPageWidget(QtWidgets.QTableWidget):
    comboBox = QtWidgets.QComboBox()
    url_edit = QtWidgets.QLineEdit()

    state_service = StateService()
    channels = state_service.get_channels()

    def __init__(self, central_widget):
        super(ChannelsPageWidget, self).__init__(central_widget)
        self.setMinimumSize(QtCore.QSize(0, 440))
        self.setObjectName("channels_page_widget")
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
        horizontal_layout.setObjectName("channels_horizontal_layout")

        self.comboBox.setParent(central_widget)
        for hosting in Hosting:
            self.comboBox.addItem(hosting.name)
        self.comboBox.setMaximumWidth(90)
        self.comboBox.setMinimumWidth(89)
        self.comboBox.setObjectName("comboBox")

        horizontal_layout.addWidget(self.comboBox)
        self.url_edit.setParent(central_widget)
        self.url_edit.setObjectName("url_edit")
        horizontal_layout.addWidget(self.url_edit)
        add_button = QtWidgets.QPushButton(central_widget)
        add_button.setObjectName("add_button")
        horizontal_layout.addWidget(add_button)
        horizontal_layout.setAlignment(QtCore.Qt.AlignBottom)
        self.horizontalHeader().setStyleSheet('QHeaderView::section {border-bottom: 1px solid black;}')
        add_button.clicked.connect(self.on_add)

        item = self.horizontalHeaderItem(0)
        item.setText(get_str('videohosting'))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str('link'))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str('delete'))
        add_button.setText(get_str('add'))

        self.url_edit.setPlaceholderText(get_str('link_on_the_channel'))

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
        msg = QtWidgets.QMessageBox()

        if self.state_service.get_channel_by_url(self.url_edit.text()) is not None:
            msg.setText(get_str('channel_already_exists'))
            msg.exec_()
            error(msg.text())
            return

        validate_result = Hosting[self.comboBox.currentText()].value[0].validate_page(self.url_edit.text())

        if validate_result != 1:
            msg.setText(get_str('channel_validation_failed'))
            msg.exec_()
            error(msg.text())
            return

        self.channels.append(Channel(hosting=self.comboBox.currentText(), url=self.url_edit.text()))
        self.state_service.save_channels(self.channels)

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

    def resizeEvent(self, event):
        coef_x = self.parent().width() / 950

        column_width = int(950 * coef_x / 3)

        self.setColumnWidth(0, column_width)
        self.setColumnWidth(1, column_width)
        self.setColumnWidth(2, column_width)

        return super(ChannelsPageWidget, self).resizeEvent(event)