import os
import sys

import requests
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QDialog

from gui.widgets import LoadingButton
from gui.widgets.ShowErrorDialog import ShowErrorDialog
from gui.widgets.introduction.AcceptLoadingPackagesForm import AcceptLoadingPackagesForm
from service.LocalizationService import get_str


class UpdatePage(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(400, 200)
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontal_layout")
        label = QLabel(get_str('loading'))
        self.horizontal_layout.addWidget(label)
        button = LoadingButton.AnimatedButton(self)
        self.horizontal_layout.addWidget(button)
        self.setLayout(self.horizontal_layout)

        self.failed = True
        self.settings = settings

    def exec_(self) -> None:
        super().exec_()

        try:
            if os.name == 'nt':
                os.putenv('NODE_SKIP_PLATFORM_CHECK', '1')
                os.putenv('PLAYWRIGHT_BROWSERS_PATH', '0')
                os.system('call playwright\\driver\\playwright.cmd install chromium')
                response = requests.get(
                    'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
                    stream=True, timeout=6000)
                if response.status_code == 200:
                    with open('ffmpeg-master-latest-win64-gpl.zip', 'wb') as f:
                        f.write(response.raw.read())

                os.makedirs('dist\\Application', exist_ok=True)
                os.system(
                    f'powershell Expand-Archive -Path ffmpeg-master-latest-win64-gpl.zip -DestinationPath {os.path.abspath("dist/Application")}')
                os.remove('ffmpeg-master-latest-win64-gpl.zip')
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