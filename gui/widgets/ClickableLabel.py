import os

from PyQt5.QtWidgets import QLabel
from playwright.sync_api import sync_playwright


class ClickableLabel(QLabel):
    label = None

    def __init__(self, label, mail):
        super().__init__()
        self.setText(label)
        self.mail = mail

    def mousePressEvent(self, QMouseEvent):
        with sync_playwright() as p:
            context = p.chromium.launch(headless=False).new_context()
            page = context.new_page()
            if self.mail:
                if os.name == 'nt':
                    import pyperclip
                    pyperclip.copy(self.text())
                else:
                    try:
                        page.goto(f'mailto:{self.text()}', wait_until='commit')
                    except:
                        return
            else:
                try:
                    page.goto(self.text(), timeout=0)
                    page.wait_for_selector('#abcsaddsa', timeout=0)
                except:
                    return


