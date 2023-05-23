from io import BytesIO

from service.videohosting_service.VideohostingService import VideohostingService
from pyrogram import Client
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
from PyQt5.QtWidgets import QTableWidgetItem
from service.StateService import StateService
import json
import os


class TelegramService(VideohostingService):

    api_id = 21915718
    api_hash = "e4fda4b7d7ab5c8f27df56c71fbe44d9"

    def __init__(self):
        self.video_regex = 'https:\/\/t.me/.*\/.*'
        self.channel_regex = '.*'
        self.title_size_restriction = 100
        self.duration_restriction = 240
        self.size_restriction = 2 * 1024
        self.upload_video_formats = list(['3g2', '3gp', '3gpp', 'asf', 'avi', 'dat', 'divx', 'dv', 'f4v', 'flv', 'gif',
                                          'm2ts', 'm4v', 'mkv', 'mod', 'mov', 'mp4', 'mpe', 'mpeg', 'mpeg4', 'mpg',
                                          'mts', 'nsv', 'ogm', 'ogv', 'qt', 'tod', 'ts', 'vob', 'wmv', 'webm'])

    def get_videos_by_url(self, url, account=None):
        result = list()

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash, workdir='service/videohosting_service/tmp') as app:
            for message in app.get_chat_history(chat_id=url):
                if message.video is not None:
                    result.append(VideoModel(url=message.link, name=message.caption, date=str(message.date)))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите номер телефона')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, phone_number, password=None):
        app = Client(name=phone_number, api_id=self.api_id, api_hash=self.api_hash, workdir='service/videohosting_service/tmp')

        app.connect()

        if app.is_initialized is not True:

            sent_code_info = app.send_code(phone_number)
            phone_code = self.handle_auth()

            app.sign_in(phone_number, sent_code_info.phone_code_hash, phone_code)

        return True

    def upload_video(self, account, file_path, name, description, destination=None):

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash, workdir='service/videohosting_service/tmp') as app:
            app.send_video(chat_id=destination, video=file_path, caption=name)

    def download_video(self, url, hosting, video_quality, format, account=None, table_item: QTableWidgetItem = None):

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                    workdir='service/videohosting_service/tmp') as app:
            chat_id = url.split('/')[3]
            message_id = url.split('/')[4]

            def progress(current, total):
                table_item.setText(f"{current * 100 / total:.1f}%")

            msg = app.get_messages(chat_id=chat_id, message_ids=int(message_id))

            result = app.download_media(msg,
                                        file_name=f'{StateService.settings.download_dir}/{hosting}/{chat_id}_{message_id}.mp4',
                                        progress=progress)

            data = {"title": msg.caption}

            with open(os.path.splitext(result)[0] + '.info.json', 'w') as f:
                json.dump(data, f)

            return result

    def get_video_info(self, url, video_quality, account=None):

        with Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                    workdir='service/videohosting_service/tmp') as app:
            chat_id = url.split('/')[3]
            message_id = url.split('/')[4]


            msg = app.get_messages(chat_id=chat_id, message_ids=int(message_id))

            return {
                'title': msg.caption,
                'description': None,
                'duration': msg.video.duration,
                'filesize': msg.video.file_size/1024**2,
                'ext': msg.video.mime_type.split('/')[1]
            }

    def handle_auth(self):
        form = AuthenticationConfirmationForm(self.login_form)
        form.exec_()

        return form.code_edit.text()

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True

    def is_async(self) -> bool:
        return True
