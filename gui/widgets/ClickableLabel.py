import os

from PyQt5.QtWidgets import QLabel
import webbrowser

class ClickableLabel(QLabel):
    label = None

    def __init__(self, label, mail):
        super().__init__()
        self.setText(label)
        self.mail = mail

    def mousePressEvent(self, QMouseEvent):
        if self.mail:
            if os.name == 'nt':
                import pyperclip
                pyperclip.copy(self.text())
            else:
                try:
                    webbrowser.open_new_tab(f'mailto:{self.text()}')
                except:
                    return
        else:
            try:
                webbrowser.open_new(self.text())
            except:
                return

