import sys
from PyQt5 import QtCore, QtGui, QtWidgets


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    BuharVideoUploader = QtWidgets.QMainWindow()

    from main import Ui_BuharVideoUploader

    ui = Ui_BuharVideoUploader()
    ui.setupUi(BuharVideoUploader)
    BuharVideoUploader.show()
    sys.exit(app.exec_())

