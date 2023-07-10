import os
import time
import uuid

from PyQt5.QtWidgets import QTableWidgetItem
from ffmpeg import FFmpeg
from googletrans import Translator
from instagrapi import Client

from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
from service.LocalizationService import get_str
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import re


class InstagramService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.instagram.com\/p\/.*\/'
        self.channel_regex = 'https:\/\/www.instagram.com\/.*'
        self.upload_video_formats = list(['mp4', 'mov'])
        self.duration_restriction = 1
        self.size_restriction = 100
        self.title_size_restriction = 2_200
        self.min_title_size = 0

    def get_videos_by_url(self, url:str, account=None):
        result = list()

        cl = Client(settings=account.auth)
        'https://www.instagram.com/nahutor/'
        splitted_url = url.split('/')

        if splitted_url[len(splitted_url) - 1] != '':
            url = splitted_url[len(splitted_url) - 1]
        else:
            url = splitted_url[len(splitted_url) - 2]


        for media in cl.user_medias_v1(int(cl.user_info_by_username_v1(url).pk)):
            result.append(VideoModel(url=f'https://www.instagram.com/p/{media.code}/',
                                     name=media.caption_text,
                                     date=str(media.taken_at)))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите пароль')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):

        cl = Client()
        cl.challenge_code_handler = self.handle_auth
        cl.login(login, password)

        return cl.get_settings()

    def handle_auth(self, username, choice):

        form = AuthenticationConfirmationForm(self.login_form)

        form.exec_()
        if form.passed is True:
            return form.code_edit.text()
        else:
            return ''

    def need_to_pass_channel_after_login(self):
        return False

    def check_auth(self, account) -> bool:
        cl = Client(settings=account.auth)

        return True

    def upload_video(self, account, file_path, name, description, destination=None,
                     table_item: QTableWidgetItem = None):
        if table_item is not None:
            table_item.setText(get_str('preparing'))
        cl = Client(settings=account.auth)

        key = uuid.uuid4()
        final_path = f'{os.path.dirname(file_path)}/{key}.mp4'
        try:
            ffmpeg = (FFmpeg(
                executable=f'{self.state_service.settings.ffmpeg}/bin/ffmpeg')
                      .input(file_path)
                      .option('y')
                      .output(final_path)
                      )
            ffmpeg.execute()
            if table_item is not None:
                table_item.setText(get_str('uploading'))
            cl.video_upload(final_path, caption=name)
        finally:
            if ffmpeg._executed:
                ffmpeg.terminate()
            if os.path.exists(final_path):
                os.remove(final_path)
            else:
                raise Exception
            if os.path.exists(f'{os.path.dirname(file_path)}/{key}.mp4.jpg'):
                os.remove(f'{os.path.dirname(file_path)}/{key}.mp4.jpg')
            else:
                raise Exception