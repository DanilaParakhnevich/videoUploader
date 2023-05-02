from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from yt_dlp import YoutubeDL
from datetime import datetime
from playwright.sync_api import sync_playwright


class RutubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:/\/rutube.ru\/video\/.*'
        self.channel_regex = 'https:\/\/rutube.ru\/.*\/videos\/'

    def get_videos_by_link(self, link, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            info = ydl.extract_info('https://rutube.ru/channel/25933729/videos/')
            for item in info['entries']:
                result.append(VideoModel(item['url'], item['title']
                                         , datetime.fromtimestamp(item['timestamp']).__str__()))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите название аккаунта')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://rutube.ru')
            page.wait_for_selector('.freyja_char-base-button__pointerCursor__JNA7y')
            page.click('.freyja_char-base-button__pointerCursor__JNA7y')
            page.wait_for_selector('.freyja_char-button__button__c4Dm-')
            page.click('.freyja_char-button__button__c4Dm-')

            page.wait_for_selector('.freyja_char-header-user-menu__userAvatar__p5-3v freyja_char-header-user-menu__userAvatarNoMargin__6zVk8', timeout=0)

            page.screenshot(path="s1.jpg")
            return page.context.cookies()
