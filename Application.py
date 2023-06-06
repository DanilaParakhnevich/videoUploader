import sys

from PyQt5 import QtWidgets
import os
import requests

from gui.widgets.ExistsNewVersionDialog import ExistsNewVersionDialog
from gui.widgets.introduction.AcceptLoadingPackagesForm import AcceptLoadingPackagesForm
from service.VersionService import VersionService

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    BuxarVideoUploader = QtWidgets.QMainWindow()

    from gui.MainPage import Ui_BuxarVideoUploader

    # Подгрузка зависимостей
    try:
        open(os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/LICENSE.txt'))
    except:
        failed = False
        while True:
            form = AcceptLoadingPackagesForm(failed)
            form.exec_()

            if form.accept:
                try:

                    if os.name.__contains__('Windows'):
                        os.system('PLAYWRIGHT_BROWSERS_PATH=0 sh playwright/driver/playwright.sh install chromium')

                        response = requests.get(
                            'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
                            stream=True, timeout=3000)
                        if response.status_code == 200:
                            with open('ffmpeg-master-latest-win64-gpl.zip', 'wb') as f:
                                f.write(response.raw.read())

                        os.system(f'mkdir {os.path.abspath("dist/")}')
                        os.system(f'mkdir {os.path.abspath("dist/Application/")}')
                        os.system(
                            f'tar -xf ffmpeg-master-latest-win64-gpl.tar.xz -C {os.path.abspath("dist/Application/")}')
                        os.system('rm ffmpeg-master-latest-win64-gpl.tar.xz')
                    else:
                        os.system('PLAYWRIGHT_BROWSERS_PATH=0 sh playwright/driver/playwright.sh install chromium')

                        response = requests.get(
                            'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz',
                            stream=True, timeout=3000)
                        if response.status_code == 200:
                            with open('ffmpeg-master-latest-linux64-gpl.tar.xz', 'wb') as f:
                                f.write(response.raw.read())

                        os.system(f'mkdir {os.path.abspath("dist/")}')
                        os.system(f'mkdir {os.path.abspath("dist/Application/")}')
                        os.system(
                            f'tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz -C {os.path.abspath("dist/Application/")}')
                        os.system('del ffmpeg-master-latest-linux64-gpl.tar.xz')

                except:
                    if os.name.__contains__('Windows'):
                        os.system('del ffmpeg-master-latest-linux64-gpl.tar.xz')
                        os.system('rmdir dist/Application/ffmpeg-master-latest-linux64-gpl/')
                        os.system('rmdir playwright/driver/package/.local-browsers')
                    else:
                        os.system('rm ffmpeg-master-latest-linux64-gpl.tar.xz')
                        os.system('rm -r dist/Application/ffmpeg-master-latest-linux64-gpl/')
                        os.system('rm -r playwright/driver/package/.local-browsers')
                    failed = True
                    form.close()
                    continue
            else:
                sys.exit(0)
            form.close()
            break

    # Проверка новой версии
    version_service = VersionService()

    current_client_version = version_service.get_current_client_version()
    current_version = version_service.get_current_version()

    if current_version != current_client_version:
        dialog = ExistsNewVersionDialog(current_version)
        dialog.exec_()

    #pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" Application.py

    ui = Ui_BuxarVideoUploader()
    ui.setupUi(BuxarVideoUploader, current_version)
    BuxarVideoUploader.show()
    sys.exit(app.exec_())