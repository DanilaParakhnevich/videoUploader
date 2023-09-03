from PyQt5 import QtWidgets, QtCore


class ComboBoxWithCompleter(QtWidgets.QComboBox):

    def __init__(self):
        super().__init__()
        completer = QtWidgets.QCompleter()
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionColumn(1)
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setCompleter(completer)
