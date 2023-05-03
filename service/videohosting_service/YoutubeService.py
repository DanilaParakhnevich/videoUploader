from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import scrapetube


class YoutubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.youtube.com\/watch?v=.*'
        self.channel_regex = '(https:\/\/www.youtube.com\/@.*)|(https:\/\/www.youtube.com\/channel\/)'

    def get_videos_by_url(self, url, account=None):
        c = scrapetube.get_channel(channel_url=url)
        result = list()
        for video in c:
            url = f'https://www.youtube.com/{video["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]}'
            result.append(VideoModel(url, video['title']['runs'][0]['text'], video['publishedTimeText']['simpleText']))
        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите телефон или адрес эл. почты')
        self.login_form.exec_()
        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://youtube.com', wait_until='commit')
            page.wait_for_selector('a[aria-label="Sign in"]')
            page.click('a[aria-label="Sign in"]')
            page.wait_for_selector('#avatar-btn', timeout=0)

            return page.context.cookies()
