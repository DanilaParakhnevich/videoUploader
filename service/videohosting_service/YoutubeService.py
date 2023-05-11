import time

from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import scrapetube


class YoutubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.youtube.com\/watch\?v=.*'
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

    def upload_video(self, account, file_path, name, description, destination=None):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://www.youtube.com/')

            page.wait_for_selector('.yt-simple-endpoint.style-scope.ytd-topbar-menu-button-renderer',
                                   timeout=10_000).click()
            page.query_selector_all('.yt-simple-endpoint.style-scope.ytd-compact-link-renderer')[0].click()
            with page.expect_file_chooser() as fc_info:
                page.query_selector(selector='#select-files-button').click()
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            page.wait_for_selector('#input', timeout=300_000)

            page.query_selector('#title-textarea').click(click_count=3)
            page.keyboard.press("Backspace")
            page.query_selector('#title-textarea').type(text=name)

            page.query_selector('#description-textarea').click()
            page.query_selector('#description-textarea').type(text=description)

            page.click(selector='#next-button')

            page.click(selector='[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]')

            page.click(selector='#next-button')
            page.click(selector='#next-button')
            page.click(selector='#next-button')

            page.click(selector='[name=PUBLIC]')

            page.click(selector='#done-button', timeout=0)

            time.sleep(1)
