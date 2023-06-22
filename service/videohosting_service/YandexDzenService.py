import time
from datetime import datetime

from PyQt5.QtWidgets import QTableWidgetItem

from service.LocalizationService import get_str
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from yt_dlp import YoutubeDL
from playwright.sync_api import sync_playwright

from service.videohosting_service.exception.NeedCreateSomeActionOnVideohostingException import \
    NeedCreateSomeActionOnVideohostingException


class YandexDzenService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/dzen.ru\/video\/watch\/.*'
        self.channel_regex = '(https:\/\/dzen.ru\/id\/.*)|(https:\/\/dzen.ru\/.*\/)'
        self.title_size_restriction = 200
        self.min_title_size = 0
        self.size_restriction = 30 * 1024
        self.duration_restriction = 240
        self.upload_video_formats = list(['3gpp', 'x-fvl', 'mp4', 'webm', 'x-ms-wmv', 'x-ms-asf', 'ogg', 'mpeg',
                                          'quicktime', 'x-m4v', 'x-msvideo', 'mkv'])

    def get_videos_by_url(self, url, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            info = ydl.extract_info(url)
            for item in info['entries']:
                result.append(VideoModel(item['url'], get_str('no_info'), get_str('no_info')))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите название аккаунта')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://passport.yandex.ru/auth/welcome', timeout=0)
            page.keyboard.press('Enter')
            page.wait_for_selector('.Section_link__pZJDa', timeout=0)

            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False
    
    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            if table_item is not None:
                table_item.setText(get_str('preparing'))
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://dzen.ru/profile/editor/create#video-editor', timeout=0)

            page.wait_for_selector('.author-studio-header__addButton-1Z.author-studio-header__rightItemButton-3a', timeout=60_000)
            page.click('.author-studio-header__addButton-1Z.author-studio-header__rightItemButton-3a')

            page.wait_for_selector('.ui-lib-context-menu__item.new-publication-dropdown__button-rl')
            page.query_selector_all('.ui-lib-context-menu__item.new-publication-dropdown__button-rl')[2].click()

            with page.expect_file_chooser() as fc_info:
                page.click('.base-button__rootElement-75.base-button__xl-28.base-button__accentPrimary-B4', timeout=0)
            if table_item is not None:
                table_item.setText(get_str('uploading'))
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            if table_item is not None:
                table_item.setText(get_str('ending'))
            page.click('.ql-editor', click_count=3)

            page.keyboard.type(text=name)

            page.click(
                '.form-actions__action-15.base-button__rootElement-75.base-button__l-3Z.base-button__accentPrimary-B4',
                timeout=0)

            time.sleep(1)

            if page.query_selector('.prepublish-popup-publisher-data__content') is not None:
                raise NeedCreateSomeActionOnVideohostingException(get_str('need_make_some_action_on_videohosting'))

    def check_auth(self, account) -> bool:
        for auth in account.auth:
            if auth['name'] == 'yandex_login':
                if datetime.utcfromtimestamp(auth['expires']) > datetime.now():
                    return True
                else:
                    return False

        return False