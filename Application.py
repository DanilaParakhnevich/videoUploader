import sys
import traceback

from PyQt5 import QtWidgets
import os
import requests


if __name__ == "__main__":
    try:
        os.system('PLAYWRIGHT_BROWSERS_PATH=0 sh playwright/driver/playwright.sh install chromium')
    except:
        print(traceback.format_exc())

    try:
        open(os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/LICENSE.txt'))
    except:
        response = requests.get('https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz', stream=True)
        if response.status_code == 200:
            with open('ffmpeg-master-latest-linux64-gpl.tar.xz', 'wb') as f:
                f.write(response.raw.read())

        os.system(f'mkdir {os.path.abspath("dist/")}')
        os.system(f'mkdir {os.path.abspath("dist/Application/")}')
        os.system(f'tar xf ffmpeg-master-latest-linux64-gpl.tar.xz -C {os.path.abspath("dist/Application/")}')
        os.system('rm ffmpeg-master-latest-linux64-gpl.tar.xz')

    #pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" Application.py

    app = QtWidgets.QApplication(sys.argv)
    BuxarVideoUploader = QtWidgets.QMainWindow()
    BuxarVideoUploader.setObjectName('BuxarVideoUploader')

    from gui.MainPage import Ui_BuxarVideoUploader

    ui = Ui_BuxarVideoUploader()
    ui.setupUi(BuxarVideoUploader)
    BuxarVideoUploader.show()
    sys.exit(app.exec_())
