from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import time


class FacebookService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.facebook.com\/watch\/\?v=.*'
        self.channel_regex = '(https:\/\/www.facebook.com\/watch\/.*\/.*)|(https:\/\/www.facebook.com\/.*\/videos)|(https:\/\/www.facebook.com\/.*sk=videos)'
        self.upload_video_formats = list(['3g2', '3gp', '3gpp', 'asf', 'avi', 'dat', 'divx', 'dv', 'f4v', 'flv', 'gif',
                                          'm2ts', 'm4v', 'mkv', 'mod', 'mov', 'mp4', 'mpe', 'mpeg', 'mpeg4', 'mpg',
                                          'mts', 'nsv', 'ogm', 'ogv', 'qt', 'tod', 'ts', 'vob', 'wmv', 'webm'])
        self.duration_restriction = 240
        self.size_restriction = 4 * 1024
        self.title_size_restriction = 9_999_999_999

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url)
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

            page.wait_for_selector('#mbasic_inline_feed_composer', timeout=0)
            return page.context.cookies()

    def upload_video(self, account, file_path, name, description, destination=None):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://www.facebook.com/')

            page.query_selector_all('.x6s0dn4.x78zum5.xl56j7k.x1rfph6h.x6ikm8r.x10wlt62')[1].click()

            with page.expect_file_chooser() as fc_info:
                page.click(
                    selector='.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x5yr21d')
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            page.query_selector('[role="textbox"]').click()
            page.keyboard.type(name)

            page.query_selector('[role="button"][aria-label="Post"]').click()

            time.sleep(5)
