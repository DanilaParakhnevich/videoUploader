from PyQt5 import QtCore, QtGui, QtWidgets

_translate = QtCore.QCoreApplication.translate

def createTableWidget(ui):
    ui.tab = QtWidgets.QWidget()
    ui.tab.setObjectName("tab")

    tableWidget = QtWidgets.QTableWidget(ui.tab)
    tableWidget.setGeometry(QtCore.QRect(20, 80, 411, 421))
    tableWidget.setObjectName("tableWidget")
    tableWidget.setColumnCount(4)
    tableWidget.setRowCount(0)
    item = QtWidgets.QTableWidgetItem()
    tableWidget.setHorizontalHeaderItem(0, item)
    item = QtWidgets.QTableWidgetItem()
    tableWidget.setHorizontalHeaderItem(1, item)
    item = QtWidgets.QTableWidgetItem()
    tableWidget.setHorizontalHeaderItem(2, item)
    item = QtWidgets.QTableWidgetItem()
    tableWidget.setHorizontalHeaderItem(3, item)
    item = tableWidget.horizontalHeaderItem(0)
    item.setText(_translate("BuharVideoUploader", "Название"))
    item = tableWidget.horizontalHeaderItem(1)
    item.setText(_translate("BuharVideoUploader", "Ссылка"))
    item = tableWidget.horizontalHeaderItem(2)
    item.setText(_translate("BuharVideoUploader", "Дата"))
    item = tableWidget.horizontalHeaderItem(3)
    item.setText(_translate("BuharVideoUploader", "Качать?"))
    return tableWidget

#todo вынести общую логику
def createTabWidget(ui):
        tabWidget = QtWidgets.QTabWidget(ui.centralwidget)
        tabWidget.setObjectName("tabWidget")
        tab = QtWidgets.QWidget()
        tab.setObjectName("tab")
        textBrowser = QtWidgets.QTextBrowser(tab)
        textBrowser.setGeometry(QtCore.QRect(700, 0, 201, 31))
        textBrowser.setObjectName("textBrowser")
        comboBox = QtWidgets.QComboBox(tab)
        comboBox.setGeometry(QtCore.QRect(700, 30, 201, 30))
        comboBox.setObjectName("comboBox")
        textBrowser_3 = QtWidgets.QTextBrowser(tab)
        textBrowser_3.setGeometry(QtCore.QRect(20, 10, 201, 31))
        textBrowser_3.setObjectName("textBrowser_3")
        lineEdit = QtWidgets.QLineEdit(tab)
        lineEdit.setGeometry(QtCore.QRect(20, 40, 591, 30))
        lineEdit.setObjectName("lineEdit")
        pushButton_5 = QtWidgets.QPushButton(tab)
        pushButton_5.setGeometry(QtCore.QRect(620, 40, 51, 30))
        pushButton_5.setObjectName("pushButton_5")
        tabWidget.addTab(tab, "")
        textBrowser.setHtml(_translate("BuharVideoUploader", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Fira Sans Semi-Light\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Видеохостинг</p></body></html>"))
        textBrowser_3.setHtml(_translate("BuharVideoUploader", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Fira Sans Semi-Light\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ссылка</p></body></html>"))
        pushButton_5.setText(_translate("BuharVideoUploader", "Go"))
        tabWidget.setTabText(tabWidget.indexOf(tab), _translate("BuharVideoUploader", "Вкладка 1"))

        return tabWidget