import os
import uuid

from PyQt5.QtWidgets import QTableWidgetItem
from ffmpeg import FFmpeg
from googletrans import Translator
from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice

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

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p, True, True)

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            page.goto(url, wait_until='networkidle', timeout=0)
            page.wait_for_selector('[role="tablist"]', timeout=40_000)
            self.scroll_page_to_the_bottom(page=page)
            stream_boxes = page.locator("//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd')]")
            translator = Translator()

            for box in stream_boxes.element_handles():
                svg = box.query_selector('svg')

                if svg is not None:
                    aria_label = svg.get_attribute('aria-label')

                    if translator.translate(aria_label).text == 'Clip' or translator.translate(
                            aria_label).text == 'Video':

                        aagu = box.query_selector('._aagu')
                        not_parsed_date = aagu.query_selector('img').get_property('alt')
                        if re.search(' on (.*).', str(not_parsed_date)) is not None:
                            date = re.search(' on (.*).', str(aagu.query_selector('img').get_property('alt'))).group(1)
                        else:
                            date = get_str('no_info')

                        result.append(
                            VideoModel(url=f'https://www.instagram.com{box.get_attribute("href")}',
                                       name=get_str('no_info'),
                                       date=date))

            return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(form, hosting, self, 2, get_str('enter_login'), get_str('enter_pas'), username_val=login, password_val=password, relogin=can_relogin)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            cl = Client()

            cl.login(login, password)
            cl.challenge_code_handler = self.challenge_code_handler
            cl.dump_settings(f'service/videohosting_service/tmp/{login.split(".")[0]}.json')

            return True

    def challenge_code_handler(self, username, choice):
        form = AuthenticationConfirmationForm(self.login_form)
        form.exec_()

        return form.code_edit.text()

    def need_to_pass_channel_after_login(self):
        return False

    def check_auth(self, account) -> bool:
        try:
            cl = Client()
            cl.load_settings(f'service/videohosting_service/tmp/{account.login.split(".")[0]}.json')
            cl.login(account.login, account.password)
            return True
        except:
            return False

    def upload_video(self, account, file_path, name, description, destination=None,
                     table_item: QTableWidgetItem = None):
        if table_item is not None:
            table_item.setText(get_str('preparing'))

        cl = Client()
        cl.load_settings(f'service/videohosting_service/tmp/{account.login.split(".")[0]}.json')
        cl.login(account.login, account.password)
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

        # pillow
        # moviepy