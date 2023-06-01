from service.LocalizationService import get_str
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
from instagrapi import Client
import re


class InstagramService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.instagram.com\/p\/.*\/'
        self.channel_regex = 'https:\/\/www.instagram.com\/.*/'
        self.upload_video_formats = list(['mp4', 'mov'])
        self.duration_restriction = 1
        self.size_restriction = 100
        self.title_size_restriction = 2_200

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=self.CHROMIUM_ARGS)
            context = browser.new_context()

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            page.goto(url)
            page.wait_for_selector('.x1iyjqo2', timeout=20_000)
            self.scroll_page_to_the_bottom(page=page)
            stream_boxes = page.locator("//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd')]")

            for box in stream_boxes.element_handles():
                svg = box.query_selector('svg')

                if svg is not None:
                    aria_label = svg.get_attribute('aria-label')

                    if aria_label == 'Clip' or\
                            aria_label == 'Video':

                        aagu = box.query_selector('._aagu')
                        not_parsed_date = aagu.query_selector('img').get_property('alt')
                        if re.search(' on (.*).', str(not_parsed_date)) is not None:
                            date = re.search(' on (.*).', str(aagu.query_selector('img').get_property('alt'))).group(1)
                        else:
                            date = get_str('no_info')

                        result.append(
                            VideoModel(url=f'https://www.instagram.com{box.get_attribute("href")}',
                                       name=get_str('no_info'),
                                       date=date))

            return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите пароль')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://www.instagram.com/')
            page.type('input[name="username"]', login)
            page.type('input[name="password"]', password)
            page.click('._acap')
            page.wait_for_selector('._aauo', timeout=0)

            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False

    def upload_video(self, account, file_path, name, description, destination=None):
        cl = Client()
        cl.login(account.login, account.password)
        cl.video_upload(file_path, caption=name)

        # pillow
        # moviepy
