from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import scrapetube


class YoutubeService(VideohostingService):

    url = 'https://www.youtube.com/'

    CHROMIUM_ARGS = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--no-first-run',
        '--disable-blink-features=AutomationControlled'
    ]

    def get_videos_by_link(self, link, account=None):
        c = scrapetube.get_channel(channel_url=link)
        result = list()
        for video in c:
            link = f'{self.url}{{video["navigationEndpoint"]["commandMetadata"]["web/CommandMetadata"]}}'
            result.append(VideoModel(link, video['title']['runs'][0]['text'], video['publishedTimeText']['simpleText']))
        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите телефон или адрес эл. почти')
        self.login_form.exec_()
        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=self.CHROMIUM_ARGS, ignore_default_args=['--enable-automation'])
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://youtube.com', wait_until='commit')
            page.wait_for_selector('a[aria-label="Sign in"]')
            page.click('a[aria-label="Sign in"]')
            page.wait_for_selector('#avatar-btn', timeout=0)
            page.context.cookies()
