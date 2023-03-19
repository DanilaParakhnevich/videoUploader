import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from main import Ui_BuharVideoUploader

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BuharVideoUploader = QtWidgets.QMainWindow()
    ui = Ui_BuharVideoUploader()
    ui.setupUi(BuharVideoUploader)
    BuharVideoUploader.show()
    sys.exit(app.exec_())

