from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from yt_dlp import YoutubeDL
import json
from playwright.sync_api import sync_playwright


class YandexDzenService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/dzen.ru\/video\/watch\/.*'
        self.channel_regex = 'https:\/\/dzen.ru\/id\/.*'


    def get_videos_by_link(self, link, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context()
                page = context.new_page()
                info = ydl.extract_info(link)
                for item in info['entries']:
                    page.goto(item['url'].split('?')[0])
                    response = json.loads(
                        page.content().split('<script type="application/ld+json" nonce="">')[1].split('</script')[0])

                    result.append(VideoModel(item['url'], response['name'], response['uploadDate']))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите название аккаунта')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://passport.yandex.ru/auth/welcome')
            page.keyboard.press('Enter')
            page.wait_for_selector('.Section_link__pZJDa', timeout=0)

            return page.context.cookies()
