import hashlib
import json
from getmac import get_mac_address
import sys
import traceback

from PyQt5 import QtWidgets
import os
import requests

from gui.widgets.ConfirmExitForm import ConfirmExitForm
from gui.widgets.EnterLicenseKeyForm import EnterLicenseKeyForm
from gui.widgets.ExistsNewVersionDialog import ExistsNewVersionDialog
from gui.widgets.ShowErrorDialog import ShowErrorDialog
from gui.widgets.introduction.AcceptLoadingPackagesForm import AcceptLoadingPackagesForm
from service.LocalizationService import get_str
from service.LoggingService import log_error
from service.StateService import StateService
from service.VersionService import VersionService

if __name__ == "__main__":

    state_service = StateService()

    class MainWindow(QtWidgets.QMainWindow):

        def __init__(self):
            super().__init__()

        def resizeEvent(self, event):
            state_service.save_main_window_size(self.width(), self.height())

        def closeEvent(self, event):
            download_queue_media = state_service.get_download_queue_media()
            upload_queue_media = state_service.get_upload_queue_media()

            event.ignore()

            process = False

            for media in download_queue_media:
                if media.status == 1:
                    process = True
                    break

            for media in upload_queue_media:
                if media.status == 1:
                    process = True
                    break

            if process:
                form = ConfirmExitForm()
                form.exec_()

                if form.passed and form.confirmed is False:
                    return

            event.accept()

    app = QtWidgets.QApplication(sys.argv)
    BuxarVideoUploader = MainWindow()

    from gui.MainPage import Ui_BuxarVideoUploader

    version_service = VersionService()

    current_client_version = version_service.get_current_client_version()
    settings = state_service.get_settings()

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

                        os.putenv('NODE_SKIP_PLATFORM_CHECK', '1')
                        os.putenv('PLAYWRIGHT_BROWSERS_PATH', '0')
                        os.system('call playwright\\driver\\playwright.cmd install chromium')
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

    activated = False

    if hasattr(settings, 'encrypted_key') and hasattr(settings, 'user_mail'):
        hash = hashlib.sha256()
        result = requests.post('http://bvu.buxarnet.ru/lc/chek.php', data={'version': current_client_version, 'encrypted_key': settings.encrypted_key, 'mac_id': get_mac_address(), 'mail': settings.user_mail})

        if result.status_code == 200:
            result = json.loads(('{' + result.content.__str__().split('{')[1]).replace('\'', ''))
            if result['activated'] is True:
                arr = current_client_version.split(".")
                arr.pop(3)
                version = ".".join(arr)

                hash.update(f'{settings.encrypted_key}{version}{get_mac_address()}{settings.user_mail}{result["data"]}{result["time"]}'.encode('utf-8'))
                key = hash.hexdigest()
                activated = key == hash.hexdigest()

    while activated is False:
        form = EnterLicenseKeyForm()
        form.exec_()

        if form.passed is False:
            sys.exit(0)

        result = requests.post('http://bvu.buxarnet.ru/lc/activate.php',
                               data={'version': current_client_version, 'key': form.license,
                                     'mac_id': get_mac_address(), 'mail': form.mail})

        if result.status_code == 200:
            result = json.loads(('{' + result.content.__str__().split('{')[1]).replace('\'', ''))
            if result['activated'] is True:
                settings.user_mail = form.mail
                settings.encrypted_key = result['encrypted_key']
                state_service.save_settings(settings)
                activated = True

        if activated is False:
            dialog = ShowErrorDialog(None, get_str('activation_failed'), get_str('error'))
            dialog.exec_()
            log_error(f'Неудачная попытка активации: mac_id: {get_mac_address()}, mail: {form.mail}, license_key: {form.license}, version: {current_client_version}')

    # Проверка новой версии

    current_version = version_service.get_current_version()

    if current_version != current_client_version:
        dialog = ExistsNewVersionDialog(current_version)
        dialog.exec_()

    try:
        ui = Ui_BuxarVideoUploader()
        ui.setupUi(BuxarVideoUploader, current_version)
        BuxarVideoUploader.show()
        sys.exit(app.exec_())
    except SystemExit:
        pass
    except:
        log_error(traceback.format_exc())
