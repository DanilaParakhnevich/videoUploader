from PyQt5 import QtWidgets, QtGui
from service.StateService import StateService


# Этот ComboBox предназначен для выбора канала из числа всех доступных
class ChannelComboBox(QtWidgets.QComboBox):
    # selected_channel - ссылка выбранного канала
    def __init__(self, parent, selected_channel: str):
        super().__init__(parent)
        self.selected_channel = selected_channel
        self.state_service = StateService()

        self.update_channel_box()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.update_channel_box()
        super().mousePressEvent(e)

    def update_channel_box(self):
        self.clear()

        channels = self.state_service.get_channels()

        selected_index = -1

        for channel in channels:
            self.addItem(channel.url)

            if channel.url == self.selected_channel:
                selected_index = self.__len__() - 1

        self.setCurrentIndex(selected_index)
        self.view().update()
        self.view().repaint()
