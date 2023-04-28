from gui.widgets.LoginForm import LoginForm
from model.VideoModel import VideoModel
from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
import time


class TikTokService(VideohostingService):

    def get_videos_by_link(self, link, account=None):
        CHROMIUM_ARGS = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--disable-blink-features=AutomationControlled',
        ]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=CHROMIUM_ARGS)
            context = browser.new_context()
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(link)
            page.wait_for_selector('.tiktok-833rgq-DivShareLayoutMain')

            page.evaluate(
                """
                var intervalID = setInterval(function () {
                    var scrollingElement = (document.scrollingElement || document.body);
                    scrollingElement.scrollTop = scrollingElement.scrollHeight;
                }, 200);

                """
            )
            prev_height = None
            while True:
                curr_height = page.evaluate('(window.innerHeight + window.scrollY)')
                if not prev_height:
                    prev_height = curr_height
                    time.sleep(1)
                elif prev_height == curr_height:
                    page.evaluate('clearInterval(intervalID)')
                    break
                else:
                    prev_height = curr_height
                    time.sleep(1)
            result = list()
            stream_boxes = page.locator("//div[contains(@class, 'tiktok-x6y88p-DivItemContainerV2')]")
            for box in stream_boxes.element_handles():
                result.append(VideoModel(url=box.query_selector('.tiktok-yz6ijl-DivWrapper').query_selector('a').get_attribute('href'), name=box.query_selector('.tiktok-1wrhn5c-AMetaCaptionLine').get_attribute('title'), date='Нет информации'))
        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите название аккаунта')
        self.login_form.exec_()
        return self.login_form.account

    def login(self, login, password):
        CHROMIUM_ARGS = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--disable-blink-features=AutomationControlled'
        ]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=CHROMIUM_ARGS, ignore_default_args=['--enable-automation'])
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://www.tiktok.com/login')
            page.wait_for_selector(selector='#main-content-homepage_hot', timeout=0)
            return page.context.cookies()
