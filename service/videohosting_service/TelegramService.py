from datetime import datetime
from os.path import exists

from service.LocalizationService import get_str
from service.LoggingService import log_error
from service.videohosting_service.VideohostingService import VideohostingService
from pyrogram import Client
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
from PyQt5.QtWidgets import QTableWidgetItem
import json
import os

from service.videohosting_service.exception.NoFreeSpaceException import NoFreeSpaceException


class TelegramService(VideohostingService):
    api_id = 21915718
    api_hash = "e4fda4b7d7ab5c8f27df56c71fbe44d9"

    def __init__(self):
        self.video_regex = 'https:\/\/t.me/.*\/.*'
        self.channel_regex = 'https://t.me/.*'
        self.title_size_restriction = 100
        self.min_title_size = 0
        self.duration_restriction = 240
        self.size_restriction = 2 * 1024
        self.upload_video_formats = list(['3g2', '3gp', '3gpp', 'asf', 'avi', 'dat', 'divx', 'dv', 'f4v', 'flv', 'gif',
                                          'm2ts', 'm4v', 'mkv', 'mod', 'mov', 'mp4', 'mpe', 'mpeg', 'mpeg4', 'mpg',
                                          'mts', 'nsv', 'ogm', 'ogv', 'qt', 'tod', 'ts', 'vob', 'wmv', 'webm'])

    def get_videos_by_url(self, url: str, account=None):
        result = list()

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                    workdir='service/videohosting_service/tmp') as app:
            history = app.get_chat_history(chat_id=url.replace('https://t.me/', ''))
            for message in history:
                if message.video is not None:
                    message_url = f'https://t.me/c/me/{message.id}' if url == 'me' else message.link
                    result.append(VideoModel(url=message_url, name=message.caption, date=str(message.date)))

        return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):

        if can_relogin is False:
            login = ''

        while True:
            self.login_form = LoginForm(form, hosting, self, 1, 'Введите номер телефона', username_val=login, relogin=can_relogin)
            self.login_form.exec_()

            if self.login_form.account is not None and self.login_form.account.auth is not None:
                return self.login_form.account
            elif self.login_form.account is None:
                if exists(f'service/videohosting_service/tmp/{self.login_form.lineEdit_username.text()}.session'):
                    os.remove(f'service/videohosting_service/tmp/{self.login_form.lineEdit_username.text()}.session')
                return
            elif self.login_form.passed is False:
                return

            login = self.login_form.lineEdit_username.text()

    def login(self, phone_number, password=None):
        try:
            app = Client(name=phone_number, api_id=self.api_id, api_hash=self.api_hash, workdir='service/videohosting_service/tmp')

            app.connect()

            if app.is_initialized is not True:
                activated = False
                enter_auth_code = None
                while True:
                    sent_code_info = app.send_code(phone_number)
                    while True:
                        try:
                            phone_code = self.handle_auth(enter_auth_code)
                            if phone_code is False:
                                return None

                            app.sign_in(phone_number, sent_code_info.phone_code_hash, phone_code)
                            activated = True
                            break
                        except:
                            log_error('Неверно введен код')
                            enter_auth_code = get_str('reenter_auth_code')
                    if activated:
                        break
            return True
        finally:
            app.disconnect()

    def handle_auth(self, enter_auth_code):
        if enter_auth_code is not None:
            form = AuthenticationConfirmationForm(self.login_form, enter_auth_code)
        else:
            form = AuthenticationConfirmationForm(self.login_form)

        form.exec_()
        if form.passed is True:
            return form.code_edit.text()
        else:
            return False

    def validate_url_by_account(self, url: str, account) -> int:
        # with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
        #             workdir='service/videohosting_service/tmp') as app:
        pass

    def upload_video(self, account, file_path, name, description, destination: str = None, table_item: QTableWidgetItem = None):

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                    workdir='service/videohosting_service/tmp') as app:
            app.send_video(chat_id=destination.replace('https://t.me/', ''), video=file_path, caption=name)

    def download_video(self, url, hosting, manual_settings, video_quality_str, audio_quality_str, video_bitrate,
                       audio_bitrate, audio_sampling_rate, fps, video_quality, video_extension, format, download_dir,
                       account=None, table_item: QTableWidgetItem = None):

        video_info = self.get_video_info(url, video_quality=video_quality, video_extension=[5, 'mp4'],
                                         video_bitrate=video_bitrate, audio_bitrate=audio_bitrate,
                                         audio_sampling_rate=audio_sampling_rate, manual_settings=manual_settings,
                                         fps=fps, audio_quality_str=audio_quality_str, video_quality_str=video_quality_str,
                                         account=account)

        space = os.statvfs(os.path.expanduser(download_dir))
        free = space.f_bavail * space.f_frsize / 1024000

        if free - video_info['filesize'] < 100:
            raise NoFreeSpaceException(f'Нет свободного места: размер файла: {video_info["filesize"]}')

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                    workdir='service/videohosting_service/tmp') as app:
            url_splitted = url.split('/')
            chat_id = url_splitted[len(url_splitted) - 2]
            message_id = url_splitted[len(url_splitted) - 1]

            def progress(current, total):
                table_item.setText(f"{current * 100 / total:.1f}%")

            msg = app.get_messages(chat_id=chat_id, message_ids=int(message_id))

            result = app.download_media(msg,
                                        file_name=fr'{download_dir}/{hosting}/{chat_id}_{message_id}_{video_quality}.mp4',
                                        progress=progress)

            data = {"title": msg.caption}

            with open(os.path.splitext(result)[0] + '.info.json', 'w') as f:
                json.dump(data, f)

            return result

    def get_video_info(self, url: str, manual_settings, video_quality_str, audio_quality_str, video_bitrate,
                       audio_bitrate, audio_sampling_rate, fps, video_quality, video_extension, account=None):

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                    workdir='service/videohosting_service/tmp') as app:
            url_splitted = url.split('/')
            chat_id = url_splitted[len(url_splitted) - 2]
            message_id = url_splitted[len(url_splitted) - 1]

            msg = app.get_messages(chat_id=chat_id, message_ids=int(message_id))

            return {
                'title': msg.caption,
                'description': None,
                'duration': msg.video.duration,
                'filesize': msg.video.file_size / 1024 ** 2,
                'ext': msg.video.mime_type.split('/')[1],
                'is_exists_format': [True, 1080]
            }

    def check_auth(self, account) -> bool:
        return os.path.exists(f'service/videohosting_service/tmp/{account.login}.session')

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True

    def is_async(self) -> bool:
        return True
