import sys
from PyQt5 import QtWidgets
import os
import requests



if __name__ == "__main__":

    os.system('PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium')
    os.system('python3 -m pip install -U https://github.com/flashdagger/ytdlp-plugins/archive/refs/heads/dtube.zip')

    try:
        open(os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/LICENSE.txt'))
    except:
        # r = requests.get('', allow_redirects=True)
        # open('ffmpeg-master-latest-linux64-gpl.tar.xz', 'wb').write(r.content)
        response = requests.get('https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz', stream=True)
        if response.status_code == 200:
            with open('ffmpeg-master-latest-linux64-gpl.tar.xz', 'wb') as f:
                f.write(response.raw.read())
        os.system(f'tar xf ffmpeg-master-latest-linux64-gpl.tar.xz -C {os.path.abspath("dist/Application/")}')
        os.system('rm ffmpeg-master-latest-linux64-gpl.tar.xz')

    #pyinstaller --add-data "service/locale/*.json:./service/locale/" Application.py


    app = QtWidgets.QApplication(sys.argv)
    BuharVideoUploader = QtWidgets.QMainWindow()
    BuharVideoUploader.setObjectName('BuharVideoUploader')

    from gui.MainPage import Ui_BuharVideoUploader

    ui = Ui_BuharVideoUploader()
    ui.setupUi(BuharVideoUploader)
    BuharVideoUploader.show()
    sys.exit(app.exec_())
