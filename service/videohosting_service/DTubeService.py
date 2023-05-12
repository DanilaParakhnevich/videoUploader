import time

from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright


class DTubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/d.tube\/#!\/v\/.*\/.*'
        self.channel_regex = 'https:\/\/d.tube\/#!\/c\/.*'

    def get_videos_by_url(self, url, account=None):
        with sync_playwright() as p:
            page = self.new_context(p=p, headless=True).new_page()

            page.goto('https://d.tube/#!/c/captainbob')

            self.scroll_page_to_the_bottom(page=page)

            result = list()

            stream_boxes = page.locator("//div[contains(@class, 'videosnap wid-ful')]")
            for box in stream_boxes.element_handles():
                result.append(VideoModel(
                    url=box.query_selector('a').get_property('href').__str__(),
                    name=box.query_selector('.customtitlelink').text_content(),
                    date=box.query_selector('.videosnaptime').text_content().strip()))

            return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите код')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            page = context.new_page()
            page.goto('https://d.tube/#!/login')
            page.type('input[name=username]', login)
            page.type('input[name=privatekey]', password)
            page.keyboard.press('Enter')

            time.sleep(5)

            try:
                page.wait_for_selector('.ui.maingrid.content')
            except:
                raise Exception('Неправильные данные')

            return page.context.cookies()
