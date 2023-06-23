import sys
import traceback

from PyQt5 import QtWidgets
import os
import requests

from gui.widgets.ExistsNewVersionDialog import ExistsNewVersionDialog
from gui.widgets.introduction.AcceptLoadingPackagesForm import AcceptLoadingPackagesForm
from service.LoggingService import log_error
from service.StateService import StateService
from service.VersionService import VersionService

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    BuxarVideoUploader = QtWidgets.QMainWindow()

    from gui.MainPage import Ui_BuxarVideoUploader

    settings = StateService().get_settings()

    # Подгрузка зависимостей
    try:
        if os.name == 'nt':
            settings.ffmpeg = os.path.abspath('dist/Application/ffmpeg-master-latest-win64-gpl')
        else:
            settings.ffmpeg = os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl')

        open(f'{settings.ffmpeg}/LICENSE.txt')
    except:
        failed = False
        while True:
            form = AcceptLoadingPackagesForm(failed)
            form.exec_()
            if form.accept:
                try:
                    if os.name == 'nt':

                        os.system('PLAYWRIGHT_BROWSERS_PATH=0 playwright\\driver\\playwright.cmd install chromium')
                        response = requests.get(
                            'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
                            stream=True, timeout=3000)
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
                            stream=True, timeout=3000)
                        if response.status_code == 200:
                            with open('ffmpeg-master-latest-linux64-gpl.tar.xz', 'wb') as f:
                                f.write(response.raw.read())

                        os.system(f'mkdir dist')
                        os.system(f'mkdir dist/Application')
                        os.system(
                            f'tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz -C {os.path.abspath("dist/Application/")}')
                        os.system('rm ffmpeg-master-latest-linux64-gpl.tar.xz')
                except:
                    if os.name == 'nt':
                        os.remove('ffmpeg-master-latest-win64-gpl.zip')
                    else:
                        os.system('rm ffmpeg-master-latest-linux64-gpl.tar.xz')

                    os.removedirs(settings.ffmpeg)
                    os.removedirs(os.path.abspath('playwright/driver/package/.local-browsers'))

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

    # pyinstaller --add-data "service/locale/*.json:./service/locale/" --add-data "gui/widgets/button_icons/*.gif:./gui/widgets/button_icons/" Application.py
    try:
        ui = Ui_BuxarVideoUploader()
        ui.setupUi(BuxarVideoUploader, current_version)
        BuxarVideoUploader.show()
        sys.exit(app.exec_())
    except:
        print(traceback.format_exc())
        log_error(traceback.format_exc())
