from service.videohosting_service.VideohostingService import VideohostingService
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
from time import sleep


class FacebookService(VideohostingService):

    def get_videos_by_link(self, link, account=None):
        # access token https://developers.facebook.com/docs/video-api/guides/get-videos/
        return list()

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1)
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
            sleep(5)

            if len(page.context.cookies()) != 7:
                if len(page.context.cookies()) == 4:
                    form = AuthenticationConfirmationForm(self.login_form)
                    form.exec_()
                    page.type('#approvals_code', form.code_edit.text())
                    page.click('#checkpointSubmitButton')
                    sleep(2)
                    if len(page.context.cookies()) != 7:
                        raise Exception('Неправильный код подтверждения')
                else:
                    raise Exception('Неверные данные')

            page.screenshot(path="s1.jpg")
            return page.context.cookies()
