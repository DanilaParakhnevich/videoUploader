import os
import subprocess
import sys
import threading

import requests
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QDialog

from gui.widgets import LoadingButton
from gui.widgets.ShowErrorDialog import ShowErrorDialog
from gui.widgets.introduction.AcceptLoadingPackagesForm import AcceptLoadingPackagesForm
from service.LocalizationService import get_str
from service.VersionService import VersionService


class UpdatePage(QDialog):
    def __init__(self, settings):
        super().__init__()
        thread = threading.Thread(daemon=True, target=self.func)

        self.windowIconChanged.connect(thread.start)
        current_client_version = VersionService().get_current_client_version()
        self.setWindowTitle(f'BuxarVideoUploader {current_client_version}')
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet('background: rgb(255,255,255)')
        self.setFixedSize(300, 100)
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontal_layout")
        label = QLabel(get_str('loading'))
        self.horizontal_layout.addWidget(label)
        self.button = LoadingButton.AnimatedButton(self)
        self.button.setStyleSheet('background: rgb(255,255,255);border: None')
        self.horizontal_layout.addWidget(self.button)
        self.setLayout(self.horizontal_layout)

        self.failed = True
        self.settings = settings
        self.button.start_animation()

    def func(self) -> None:
        try:
            if os.name == 'nt':
                os.putenv('NODE_SKIP_PLATFORM_CHECK', '1')
                os.putenv('PLAYWRIGHT_BROWSERS_PATH', '0')
                subprocess.call([fr'{os.getcwd()}\\playwright\\driver\\playwright.cmd','install','chromium'], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, creationflags=0x08000000)
                response = requests.get(
                    'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
                    stream=True, timeout=6000)
                if response.status_code == 200:
                    with open('ffmpeg-master-latest-win64-gpl.zip', 'wb') as f:
                        f.write(response.raw.read())

                os.makedirs('dist\\Application', exist_ok=True)
                subprocess.call(
                    ['powershell', '-WindowStyle', 'hidden', 'Expand-Archive', '-Path', 'ffmpeg-master-latest-win64-gpl.zip', '-DestinationPath', rf'{os.path.abspath("dist/Application")}'], shell=False)
                os.remove('ffmpeg-master-latest-win64-gpl.zip')
                self.failed = False
            else:
                os.system('PLAYWRIGHT_BROWSERS_PATH=0 sh playwright/driver/playwright.sh install chromium')

                response = requests.get(
                    'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz',
                    stream=True, timeout=6000)
                if response.status_code == 200:
                    with open('ffmpeg-master-latest-linux64-gpl.tar.xz', 'wb') as f:
                        f.write(response.raw.read())

                os.system(f'mkdir dist')
                os.system(f'mkdir dist/Application')
                os.system(
                    f'tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz -C {os.path.abspath("dist/Application/")}')
                os.system('rm ffmpeg-master-latest-linux64-gpl.tar.xz')
                self.failed = False
        except Exception as e:

            dialog = ShowErrorDialog(None, e.args[0], get_str('error'))
            dialog.setWindowIcon(QIcon('icon.png'))
            dialog.exec_()

            if os.name == 'nt':
                os.remove('ffmpeg-master-latest-win64-gpl.zip')
            else:
                os.system('rm ffmpeg-master-latest-linux64-gpl.tar.xz')

            os.removedirs(self.settings.ffmpeg)
            os.removedirs(os.path.abspath('playwright/driver/package/.local-browsers'))

        finally:
            self.close()