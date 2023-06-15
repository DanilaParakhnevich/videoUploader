from PyQt5 import QtWidgets, QtCore

from service.LocalizationService import get_str


class VideoListWidget(QtWidgets.QTableWidget):

    comboBox = QtWidgets.QComboBox()

    def __init__(self, parent, media_list):
        super(VideoListWidget, self).__init__(parent)
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
        self.horizontalHeader().setDefaultSectionSize(155)

        for media in media_list:
            if media.status == 2:
                self.insertRow(self.rowCount())
                item1 = QtWidgets.QTableWidgetItem(media.url)
                item2 = QtWidgets.QTableWidgetItem(media.video_dir)

                item3 = QtWidgets.QTableWidgetItem()
                item3.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)
                item3.setCheckState(QtCore.Qt.Unchecked)

                self.setItem(self.rowCount() - 1, 0, item1)
                self.setItem(self.rowCount() - 1, 1, item2)
                self.setItem(self.rowCount() - 1, 2, item3)

        item = self.horizontalHeaderItem(0)
        item.setText(get_str("link"))
        item = self.horizontalHeaderItem(1)
        item.setText(get_str("video_dir"))
        item = self.horizontalHeaderItem(2)
        item.setText(get_str("is_upload"))
