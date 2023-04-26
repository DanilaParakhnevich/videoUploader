from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
from gui.widgets.LoginForm import LoginForm

from yt_dlp import YoutubeDL
from datetime import datetime

class OKService(VideohostingService):

    def get_videos_by_link(self, link, account=None):
        # https://stackoverflow.com/questions/61261777/how-to-extract-video-urls-and-titles-from-ok-ru-video-using-the-cli or hard api or scrapping...
        return list()

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://ok.ru/')
            page.type('#field_email', login)
            page.type('#field_password', password)
            page.keyboard.press('Enter')

            page.wait_for_selector('.html5-upload-link', timeout=10_000)

            return page.context.cookies()


