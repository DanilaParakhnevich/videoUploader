from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import time


class FacebookService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.facebook.com\/watch\/\?v=.*'
        self.channel_regex = '(https:\/\/www.facebook.com\/watch\/.*\/.*)|(https:\/\/www.facebook.com\/.*\/videos)|(https:\/\/www.facebook.com\/.*sk=videos)'

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url, wait_until='commit')
            time.sleep(5)
            self.scroll_page_to_the_bottom(page=page, timeout=3)
            stream_boxes = page.locator("//div[contains(@class,'x6s0dn4 x78zum5 x1q0g3np x1qughib')]")

            for box in stream_boxes.element_handles():
                result.append(
                    VideoModel(url=str(box.query_selector('a').get_property('href')), name=box.query_selector('.x1lliihq').text_content(), date=box.query_selector('.xu06os2').text_content()))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://mbasic.facebook.com')
            page.type('input[name=email]', login)
            page.type('input[name=pass]', password)
            page.keyboard.press('Enter')

            page.wait_for_selector('#checkpointSubmitButton-actual-button', timeout=0)
            return page.context.cookies()
    def upload_video(self, account, file_path, name, description):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://www.facebook.com/')

            page.query_selector_all('.x6s0dn4.x78zum5.xl56j7k.x1rfph6h.x6ikm8r.x10wlt62')[1].click()



            #remain facebook...
            #retest