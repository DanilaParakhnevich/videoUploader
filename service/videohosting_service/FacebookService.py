from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import time


class FacebookService(VideohostingService):

    def get_videos_by_link(self, link, account=None):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://www.facebook.com/DerekHough/videos', wait_until='commit')
            time.sleep(5)

            page.evaluate(
                """
                var intervalID = setInterval(function () {
                    var scrollingElement = (document.scrollingElement || document.body);
                    scrollingElement.scrollTop = scrollingElement.scrollHeight;
                }, 200);

                """
            )
            prev_height = None
            attempt = 1
            while True:
                curr_height = page.evaluate('(window.innerHeight + window.scrollY)')
                if not prev_height:
                    prev_height = curr_height
                    time.sleep(3)
                elif prev_height == curr_height:
                    if attempt != 1:
                        page.evaluate('clearInterval(intervalID)')
                        break
                    else:
                        attempt += 1
                else:
                    prev_height = curr_height
                    time.sleep(3)
                    attempt = 1

            result = list()
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
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://mbasic.facebook.com')
            page.type('input[name=email]', login)
            page.type('input[name=pass]', password)
            page.keyboard.press('Enter')
            time.sleep(5)

            if len(page.context.cookies()) != 7:
                if len(page.context.cookies()) == 4:
                    form = AuthenticationConfirmationForm(self.login_form)
                    form.exec_()
                    page.type('#approvals_code', form.code_edit.text())
                    page.click('#checkpointSubmitButton')
                    time.sleep(2)
                    try:
                        page.wait_for_selector('#checkpointSubmitButton', timeout=1_000)
                        page.click('#checkpointSubmitButton')
                    except:
                        print('bad')

                    try:
                        page.wait_for_selector('#checkpointSubmitButton-actual-button', timeout=1_000)
                        page.click('#checkpointSubmitButton-actual-button')
                        page.click('#checkpointSubmitButton-actual-button')
                        page.click('#checkpointSubmitButton-actual-button')


                    except:
                        print('bad')

                    if len(page.context.cookies()) < 7:
                        raise Exception('Неправильный код подтверждения')
                else:
                    raise Exception('Неверные данные')

            page.screenshot(path="s1.jpg")
            return page.context.cookies()
