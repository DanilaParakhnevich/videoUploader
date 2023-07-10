import time
from datetime import datetime

from PyQt5.QtWidgets import QTableWidgetItem

from gui.widgets.LoginForm import LoginForm
from model.VideoModel import VideoModel
from service.LocalizationService import get_str
from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
from service.Tiktok_uploader import uploadVideo


class TikTokService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https://www.tiktok.com/.*/video/.*'
        self.channel_regex = 'https://www.tiktok.com/.*'
        self.title_size_restriction = 2_200
        self.min_title_size = 0
        self.duration_restriction = 30
        self.size_restriction = 2 * 1024
        self.upload_video_formats = list(['mp4', 'webm'])

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url)
            page.wait_for_selector('[data-e2e="user-post-item-list"]', timeout=0)

            self.scroll_page_to_the_bottom(page=page)

            elements = page.query_selector_all('[data-e2e="user-post-item-desc"]')
            for box in elements:
                result.append(VideoModel(url=box.query_selector('a').get_attribute('href'),
                                         name=box.query_selector('a').get_attribute('title'),
                                         date=get_str('no_info')))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите название аккаунта')
        self.login_form.exec_()
        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://www.tiktok.com/login')
            page.wait_for_selector(selector='#main-content-homepage_hot', timeout=0)
            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False

    # Пришлось использовать готовое чужое решение для выгрузки видео для TikTok, тк на сайте хорошая защита от ботов
    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        table_item.setText(get_str('preparing'))
        for cookie in account.auth:
            if cookie['name'] == 'sessionid':
                table_item.setText(get_str('uploading'))
                uploadVideo(session_id=cookie['value'], video=file_path, title=name, tags=list())
                return

        raise Exception('Что-то пошло не так')

    def check_auth(self, account) -> bool:
        for auth in account.auth:
            if auth['name'] == 'sessionid':
                if datetime.utcfromtimestamp(auth['expires']) > datetime.now():
                    return True
                else:
                    return False

        return False
