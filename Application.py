import hashlib
import json

from PyQt5.QtGui import QIcon
from getmac import get_mac_address
import sys
import traceback

from PyQt5 import QtWidgets
import os
import requests
from requests import ConnectionError

from gui.UpdatePage import UpdatePage
from gui.widgets.ConfirmExitForm import ConfirmExitForm
from gui.widgets.EnterLicenseKeyForm import EnterLicenseKeyForm
from gui.widgets.ExistsNewVersionDialog import ExistsNewVersionDialog
from gui.widgets.ShowErrorDialog import ShowErrorDialog
from gui.widgets.introduction.AcceptLoadingPackagesForm import AcceptLoadingPackagesForm
from service.LocalizationService import get_str
from service.LoggingService import log_error
from service.MailService import MailService
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
                form.setWindowIcon(QIcon('icon.png'))
                form.exec_()

                if form.passed is False or form.confirmed is False:
                    return

            event.accept()
    try:
        app = QtWidgets.QApplication(sys.argv)
        BuxarVideoUploader = MainWindow()
        BuxarVideoUploader.setWindowIcon(QIcon('icon.png'))

        from gui.MainPage import Ui_BuxarVideoUploader

        version_service = VersionService()

        current_client_version = version_service.get_current_client_version()
        settings = state_service.get_settings()

        activated = False

        license_model = state_service.get_license_model()
        try:
            if license_model.encrypted_key is not None and license_model.user_mail is not None:
                hash = hashlib.sha256()
                result = requests.post('http://bvu.buxarnet.ru/lc/chek.php', data={'version': current_client_version, 'encrypted_key': "".join(license_model.encrypted_key), 'mac_id': get_mac_address(), 'mail': "".join(license_model.user_mail)})

                if result.status_code == 200:
                    result = json.loads(('{' + result.content.__str__().split('{')[1]).replace('\'', ''))
                    if result['activated'] is True:
                        arr = current_client_version.split(".")
                        arr.pop(3)
                        version = ".".join(arr)

                        hash.update(f'{"".join(license_model.encrypted_key)}{version}{get_mac_address()}{"".join(license_model.user_mail)}{result["data"]}{result["time"]}'.encode('utf-8'))
                        key = hash.hexdigest()
                        activated = key == result['chek']
                if activated is False:
                    log_error(f'Неудачная валидация лицензии: encrypted_key: {"".join(license_model.encrypted_key)}, mac_id: {get_mac_address()}, mail: {license_model.user_mail[0]}, version: {"".join(current_client_version)}')
            count = 0
            while activated is False:
                form = EnterLicenseKeyForm()
                form.setWindowIcon(QIcon('icon.png'))
                form.exec_()

                if form.passed is False:
                    sys.exit(0)

                result = requests.post('http://bvu.buxarnet.ru/lc/activate.php',
                                       data={'version': current_client_version, 'key': form.license,
                                             'mac_id': get_mac_address(), 'mail': form.mail})

                if result.status_code == 200:
                    result = json.loads(('{' + result.content.__str__().split('{')[1]).replace('\'', ''))
                    if result['activated'] is True:
                        license_model.user_mail = list(form.mail)
                        license_model.encrypted_key = list(result['encrypted_key'])
                        state_service.save_license_model(license_model)
                        activated = True
                        MailService().send_mail(f'Лицензия активирована: mac_id: {get_mac_address()}, mail: {form.mail}, license_key: {form.license}, version: {current_client_version}')

                if activated is False:
                    count += 1
                    dialog = ShowErrorDialog(None, get_str('activation_failed'), get_str('error'))
                    dialog.exec_()
                    log_error(f'Неудачная попытка активации: mac_id: {get_mac_address()}, mail: {form.mail}, license_key: {form.license}, version: {current_client_version}')
                    if count >= 5:
                        log_error(f'Возможна попытка взлома: mac_id: {get_mac_address()}, mail: {form.mail}, license_key: {form.license}, version: {current_client_version}')
                    MailService().send_log()
        except ConnectionError as e:
            dialog = ShowErrorDialog(None, get_str('check_internet_connection'), get_str('error'))
            dialog.exec_()
    except Exception:
        log_error(traceback.format_exc())
        MailService().send_log()
        sys.exit(-1)

    try:
        if os.name == 'nt':
            settings.ffmpeg = os.path.abspath('dist/Application/ffmpeg-master-latest-win64-gpl')
            open('driver/package/.local-browsers/chromium-1024')
        else:
            settings.ffmpeg = os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl')

        open(f'{settings.ffmpeg}/LICENSE.txt')
    except:
        failed = False
        while True:
            form = AcceptLoadingPackagesForm(failed)
            form.setWindowIcon(QIcon('icon.png'))
            form.exec_()
            if form.accept:
                update_page = UpdatePage(settings)
                update_page.exec_()

                if update_page.failed is True:
                    sys.exit(-1)

                MailService().send_mail(f'Приложение установлено: mac_id: {get_mac_address().__str__()}, version: {current_client_version}')
            else:
                sys.exit(0)
            break

    # Проверка новой версии

    current_version = version_service.get_current_version()

    if current_version != current_client_version:
        dialog = ExistsNewVersionDialog(current_version)
        dialog.setWindowIcon(QIcon('icon.png'))
        dialog.exec_()

    try:
        ui = Ui_BuxarVideoUploader()
        ui.setupUi(BuxarVideoUploader, current_client_version)
        BuxarVideoUploader.show()
        sys.exit(app.exec_())
    except SystemExit:
        pass
    except:
        log_error(traceback.format_exc())
        MailService().send_log()
