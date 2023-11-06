import time
from datetime import datetime

from PyQt5.QtWidgets import QTableWidgetItem
from googletrans import Translator

from service.LocalizationService import get_str
from service.StateService import StateService
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from yt_dlp import YoutubeDL
from playwright.sync_api import sync_playwright


class DailyMotionService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/.*dailymotion.com\/video\/.*'
        self.channel_regex = 'https:\/\/.*dailymotion.com\/.*'
        self.title_size_restriction = 255
        self.min_title_size = 0
        self.size_restriction = 4 * 1024
        self.duration_restriction = 120
        self.upload_video_formats = list(['avi', 'wmv', 'asf', 'mov', 'rm', 'rmvb', 'mpg', 'mpeg',
                                          'mpeg', 'vob', 'mp4', 'm4v', 'mkv', '3gp', 'dv', 'flv', 'f4v',
                                          'divx', 'ogg', 'ogv', 'ts', 'webm', 'mxf'])

    def get_videos_by_url(self, url: str, account=None):
        result = list()
        with YoutubeDL(self.extract_info_opts) as ydl:
            if url.endswith('/') is False:
                url = url.strip() + '/'

            info = ydl.extract_info(url)
            for item in info['entries']:
                title = get_str('no_info')
                date = get_str('no_info')
                try:
                    with sync_playwright() as p:
                        context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
                        if account is not None:
                            context.add_cookies(account.auth)
                        page = context.new_page()
                        page.goto(item['url'], timeout=0)
                        page.wait_for_selector('.PubDate__videoPubDate___3o7a-', timeout=0)
                        date = page.query_selector('.PubDate__videoPubDate___3o7a-').text_content()
                        title = page.query_selector('.NewVideoInfoTitle__videoTitle___3kiXi').text_content()
                except:
                    pass
                result.append(VideoModel(item['url'], title, date))

        return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(form, hosting, self, 2, get_str('login'), title=title, username_val=login,
                                    password_val=password, relogin=can_relogin)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)

            page = context.new_page()
            page.goto('https://www.dailymotion.com/signin', wait_until='domcontentloaded', timeout=0)

            page.wait_for_selector('.Button__button___3e-04.CookiePopup__button____eXp2', timeout=0)
            page.click('.Button__button___3e-04.CookiePopup__button____eXp2')
            page.wait_for_selector('.EmailInput__input___2Pq6c', timeout=0)
            page.query_selector('.EmailInput__input___2Pq6c').type(login)
            page.query_selector('.PasswordInput__input___2KTm0').type(password)
            page.query_selector('[data-testid="submit_button"]').click()

            page.wait_for_selector('[data-testid="logged-user-dropdown"]', timeout=0)

            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False

    def upload_video(self, account, file_path, name, description, destination=None,
                     table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            if table_item is not None:
                table_item.setText(get_str('preparing'))
            context = self.new_context(p=p, headless=StateService.settings.debug_browser is False,
                                       use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://www.dailymotion.com/library/videos', timeout=0)

            page.wait_for_selector('[data-testid="upload-banner"]', timeout=0)

            with page.expect_file_chooser() as fc_info:
                page.click('[data-testid="upload-banner"]', timeout=0)
            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            page.wait_for_selector('#title', timeout=0)
            page.click('#title', click_count=3)
            page.keyboard.press('Backspace')
            page.query_selector('#title').type(name)

            while page.query_selector('.VideoSettingsModal__saveButton___k5aKP').get_attribute('disabled') is not None:
                time.sleep(5)

            page.click('.VideoSettingsModal__saveButton___k5aKP', timeout=0)

            time.sleep(5)

    def check_auth(self, account) -> bool:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://www.dailymotion.com/', wait_until='domcontentloaded', timeout=0)

            try:
                page.wait_for_selector('[data-testid="logged-user-dropdown"]', timeout=80_000)
            except:
                return False

            return True