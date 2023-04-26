from service.videohosting_service.VideohostingService import VideohostingService
from yt_dlp import YoutubeDL
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from datetime import datetime
from playwright.sync_api import sync_playwright


class DTubeService(VideohostingService):

    extract_info_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'logger': False,
        "extract_flat": True,
    }

    def get_videos_by_link(self, link, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            info = ydl.extract_info(link)
            for item in info['entries']:
                result.append(VideoModel(f'https://d.tube/#!/v/{item["id"]}', item['title'],
                                         datetime.fromtimestamp(item['timestamp']).__str__()))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://d.tube/#!/login')
            page.type('input[name=username]', login)
            page.type('input[name=privatekey]', password)
            page.keyboard.press('Enter')

            if page.url == 'https://d.tube/#!/login':
                raise Exception('Неправильные данные')

            page.screenshot(path="s1.jpg")
            return page.context.cookies()
