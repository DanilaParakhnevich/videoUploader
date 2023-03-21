from PyQt5 import QtCore, QtWidgets
import model.hostings

comboBox = QtWidgets.QComboBox()
table_widget = QtWidgets.QTableWidget()
password_edit = QtWidgets.QLineEdit()
login_edit = QtWidgets.QLineEdit()

def setupUi(central_widget):
    table_widget.setParent(central_widget)
    table_widget.setMinimumSize(QtCore.QSize(0, 440))
    table_widget.setObjectName("table_widget")
    table_widget.setColumnCount(3)
    table_widget.setRowCount(0)
    item = QtWidgets.QTableWidgetItem()
    table_widget.setHorizontalHeaderItem(0, item)
    item = QtWidgets.QTableWidgetItem()
    table_widget.setHorizontalHeaderItem(1, item)
    item = QtWidgets.QTableWidgetItem()
    table_widget.setHorizontalHeaderItem(2, item)
    table_widget.horizontalHeader().setDefaultSectionSize(310)
    
    horizontal_layout = QtWidgets.QHBoxLayout(table_widget)
    horizontal_layout.setObjectName("horizontal_layout")

    comboBox.setParent(central_widget)
    for hosting in model.hostings.Hostings:
        comboBox.addItem(hosting.value)
    comboBox.setMinimumSize(QtCore.QSize(300, 0))
    comboBox.setObjectName("comboBox")

    horizontal_layout.addWidget(comboBox)
    login_label = QtWidgets.QLabel(central_widget)
    login_label.setObjectName("login_label")
    horizontal_layout.addWidget(login_label)
    login_edit.setParent(central_widget)
    login_edit.setObjectName("login_edit")
    horizontal_layout.addWidget(login_edit)
    password_label = QtWidgets.QLabel(central_widget)
    password_label.setObjectName("password_label")
    horizontal_layout.addWidget(password_label)
    password_edit.setParent(central_widget)
    password_edit.setObjectName("password_edit")
    horizontal_layout.addWidget(password_edit)
    add_button = QtWidgets.QPushButton(central_widget)
    add_button.setObjectName("add_button")
    horizontal_layout.addWidget(add_button)

    add_button.clicked.connect(on_add)

    _translate = QtCore.QCoreApplication.translate
    item = table_widget.horizontalHeaderItem(0)
    item.setText(_translate("BuharVideoUploader", "Видеохостинг"))
    item = table_widget.horizontalHeaderItem(1)
    item.setText(_translate("BuharVideoUploader", "Логин"))
    item = table_widget.horizontalHeaderItem(2)
    item.setText(_translate("BuharVideoUploader", "Удалить"))
    login_label.setText(_translate("BuharVideoUploader", "Логин"))
    password_label.setText(_translate("BuharVideoUploader", "Пароль"))
    add_button.setText(_translate("BuharVideoUploader", "Добавить"))

    return table_widget


def on_add():

    table_widget.insertRow(table_widget.rowCount())
    item1 = QtWidgets.QTableWidgetItem(comboBox.currentText())
    item2 = QtWidgets.QTableWidgetItem(login_edit.text())

    input_position = table_widget.rowCount() - 1

    btn = QtWidgets.QPushButton(table_widget)
    btn.setText('Удалить')
    table_widget.setCellWidget(input_position, 2, btn)

    btn.clicked.connect(on_delete_row)

    table_widget.setItem(input_position, 0, item1)
    table_widget.setItem(input_position, 1, item2)


def on_delete_row(self):#todo класс?
    button = self.sender()
    if button:
        row = table_widget.indexAt(button.pos()).row()
        table_widget.removeRow(row)
