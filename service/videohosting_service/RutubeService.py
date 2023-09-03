import time

from PyQt5.QtWidgets import QTableWidgetItem

from service.LocalizationService import get_str
from service.LoggingService import log_error
from service.StateService import StateService
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from yt_dlp import YoutubeDL
from datetime import datetime
from playwright.sync_api import sync_playwright


class RutubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:/\/rutube.ru\/video\/.*'
        self.channel_regex = 'https:\/\/rutube.ru\/channel\/.*'
        self.upload_video_formats = list(['mp4', 'flv', 'avi', 'mov', 'mpg', 'wmv', 'm4v', 'mp3',
                                          'wma', '3gp', 'mkv', 'webm'])
        self.duration_restriction = 300
        self.size_restriction = 10 * 1024
        self.min_title_size = 1
        self.title_size_restriction = 100
        self.description_size_restriction = 5_000

    def get_videos_by_url(self, url: str, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            url = url if url.__contains__('videos') else url + 'videos'
            info = ydl.extract_info(url)
            for item in info['entries']:
                result.append(VideoModel(item['url'], item['title']
                                         , datetime.fromtimestamp(item['timestamp']).__str__()))

        return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(None, hosting, self, 2, get_str('enter_login'), title=title, username_val=login, password_val=password, relogin=can_relogin)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://studio.rutube.ru/', timeout=0, wait_until='commit')

            page.wait_for_selector('#phone-or-email-login', timeout=0)

            page.query_selector('#phone-or-email-login').type(login, timeout=0)
            time.sleep(3)
            page.query_selector('#submit-login-continue').click()
            time.sleep(3)
            page.wait_for_selector('#login-password', timeout=0)
            page.query_selector('#login-password').type(password, timeout=0)
            page.click(
                '.freyja_char-base-button__btnContent__3vr55.freyja_char-base-button__btnContent-icon-left__3L4yd')

            page.wait_for_selector('.pen-page-header_main-header.pen-page-header_color-default.pen-page-header_size-default.pen-page-header_margin-top', timeout=0)

            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False

    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        if table_item is not None:
            table_item.setText(get_str('preparing'))
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=StateService.settings.debug_browser is False, use_user_agent_arg=True)
            context.add_cookies(account.auth.copy())

            page = context.new_page()
            page.goto('https://studio.rutube.ru/uploader/', timeout=0)

            try:
                page.wait_for_selector(
                    '.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__large__vS7yq.freyja_char-base-button__pointerCursor__JNA7y',
                    timeout=5_000)
            except:
                if page.query_selector('#phone-or-email-login') is not None:
                    page.query_selector('#phone-or-email-login').type(account.login, timeout=0)
                    time.sleep(3)
                    page.query_selector('#submit-login-continue').click()
                    time.sleep(3)
                    page.wait_for_selector('#login-password', timeout=0)
                    page.query_selector('#login-password').type(account.password, timeout=0)
                    page.click(
                        '.freyja_char-base-button__btnContent__3vr55.freyja_char-base-button__btnContent-icon-left__3L4yd')

            page.wait_for_selector('.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__large__vS7yq.freyja_char-base-button__pointerCursor__JNA7y', timeout=0)
            with page.expect_file_chooser() as fc_info:
                page.click(selector='.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__large__vS7yq.freyja_char-base-button__pointerCursor__JNA7y', timeout=0)
            if table_item is not None:
                table_item.setText(get_str('uploading'))
            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            if table_item is not None:
                table_item.setText(get_str('ending'))
            page.wait_for_selector('[name=title]', timeout=0)
            page.wait_for_selector('[name=description]', timeout=0)

            time.sleep(1)

            page.query_selector('[name="title"]').fill('')
            page.query_selector('[name="title"]').type(text=name, timeout=0)

            page.query_selector('[name="description"]').type(description if description is not None else '', timeout=0)

            page.click('[name="categories"]')
            page.click('.freyja_char-dropdown-layout__dropdownItem__x8JCK')

            page.wait_for_selector(
                '.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__regular__ksZLL.freyja_char-base-button__pointerCursor__JNA7y', timeout=0)

            page.click(
                selector='.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__regular__ksZLL.freyja_char-base-button__pointerCursor__JNA7y',
                timeout=0)

    def check_auth(self, account) -> bool:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://studio.rutube.ru/uploader/', wait_until='domcontentloaded', timeout=0)
            try:
                page.wait_for_selector(
                    '.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__large__vS7yq.freyja_char-base-button__pointerCursor__JNA7y',
                    timeout=5_000)
                return True
            except:
                if page.query_selector('#phone-or-email-login') is not None:
                    page.query_selector('#phone-or-email-login').type(account.login, timeout=0)
                    time.sleep(3)
                    page.query_selector('#submit-login-continue').click()
                    time.sleep(3)
                    page.wait_for_selector('#login-password', timeout=0)
                    page.query_selector('#login-password').type(account.password, timeout=0)
                    page.click(
                        '.freyja_char-base-button__btnContent__3vr55.freyja_char-base-button__btnContent-icon-left__3L4yd')

                    page.wait_for_selector('.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__large__vS7yq.freyja_char-base-button__pointerCursor__JNA7y', timeout=10_000)
                    return True
            return False
