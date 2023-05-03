from PyQt5 import QtCore, QtWidgets, QtGui
from service.StateService import StateService


class ChannelComboBox(QtWidgets.QComboBox):
    def __init__(self, t, selected_channel):
        super().__init__(t)
        self.selected_channel = selected_channel
        self.state_service = StateService()

        self.update_channel_box()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.update_channel_box()
        super().mousePressEvent(e)

    def update_channel_box(self):
        self.clear()

        selected_index = 0

        channels = self.state_service.get_channels()

        for channel in channels:
            self.addItem(channel.url)

            if channel.url == self.selected_channel:
                selected_index = self.__len__() - 1

        self.setCurrentIndex(selected_index)
        self.view().update()
        self.view().repaint()
