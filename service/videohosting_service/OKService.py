from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
from gui.widgets.LoginForm import LoginForm
import time
from model.VideoModel import VideoModel


class OKService(VideohostingService):

    def get_videos_by_link(self, link, account=None):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(link)
            page.wait_for_selector('#listBlockPanelAltGroupVideoMoviesPagingBlock')

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
            stream_boxes = page.locator("//a[contains(@class,'video-card_n')]")
            for box in stream_boxes.element_handles():
                if str(box.get_property('href')).__contains__('video'):
                    result.append(VideoModel(url=str(box.get_property('href')), name=box.inner_html(), date='Нет информации'))
        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите пароль')
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
