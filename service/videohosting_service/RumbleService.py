import time

from PyQt5.QtWidgets import QTableWidgetItem
from yt_dlp import YoutubeDL

from service.LocalizationService import get_str
from service.StateService import StateService
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright


class RumbleService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/rumble.com\/.*.html'
        self.channel_regex = '(https:\/\/rumble.com\/c\/.*)|(https:\/\/rumble.com\/user\/.*)'
        self.title_size_restriction = 255
        self.min_title_size = 0
        self.description_size_restriction = 999999
        self.size_restriction = 15 * 1024
        self.upload_video_formats = list(['m4v', 'mp4', 'ogm', 'wmv', 'mpg', 'webm', 'ogv', 'mov', 'asx', 'mpeg', 'mp4', 'm4v', 'avi'])

    def get_videos_by_url(self, url, account=None):
        result = list()
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            if account is not None:
                context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url, timeout=0)
            page.wait_for_selector('.video-listing-entry')
            self.scroll_page_to_the_bottom(page=page)

            elements = page.query_selector_all('.video-listing-entry')
            for box in elements:
                result.append(VideoModel(url='https://rumble.com' + box.query_selector('.video-item--a').get_attribute('href'),
                                         name=box.query_selector('.video-item--title').text_content(),
                                         date=box.query_selector('.video-item--meta.video-item--time').text_content()))

        return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(form, hosting, self, 2, get_str('enter_login'), get_str('enter_pas'), username_val=login, password_val=password, relogin=can_relogin)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://rumble.com/', timeout=0)
            page.wait_for_selector('.header-user.round-button.transparent-button', timeout=0)
            page.click('.header-user.round-button.transparent-button')
            page.wait_for_selector('#login-username', timeout=0)
            page.type('#login-username', login)
            page.type('#login-password', password)
            page.keyboard.press('Enter')

            page.wait_for_selector('.user-image.user-image--icon.header-user-img', timeout=0)

            return page.context.cookies()

    def upload_video(self, account, file_path, name, description, destination=None,
                     table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            if table_item is not None:
                table_item.setText(get_str('preparing'))

            context = self.new_context(p=p, headless=StateService.settings.debug_browser is False,
                                       use_user_agent_arg=True)

            page = context.new_page()
            page.goto(destination, timeout=0)

            context.add_cookies(account.auth)

            page.wait_for_selector('.media-subscribe-and-notify', timeout=0)
            id = page.query_selector('.media-subscribe-and-notify').get_attribute('data-slug').replace('c-', '')

            page = context.new_page()
            page.goto('https://rumble.com/upload.php', timeout=0)

            page.wait_for_selector('.upload-video-placeholder', timeout=0)

            with page.expect_file_chooser() as fc_info:
                page.click('.upload-video-placeholder', timeout=0)
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            page.wait_for_selector('#title', timeout=0)
            page.query_selector('#title').type(name, timeout=0)
            page.query_selector('#description').type(description, timeout=0)

            for option in page.query_selector('#channelId').query_selector_all('option'):
                if option.get_attribute('value') == id:
                    page.locator('#channelId').select_option(value=option.get_attribute('value'))
                    break

            page.wait_for_selector('.num_percent')

            while page.query_selector('.num_percent').text_content().split(' ')[0] != '100%':
                time.sleep(5)

            page.query_selector('[value="Upload"]').click()

            page.wait_for_selector('[for="crights"]', timeout=0)
            page.click('[for="crights"]')
            page.click('[for="cterms"]')

            try:
                page.query_selector('[value="Submit"]').click()
                page.wait_for_selector('#view', timeout=80_000)
            except:
                raise Exception('Дубликат')

            time.sleep(5)

    def check_auth(self, account) -> bool:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://rumble.com/', wait_until='domcontentloaded', timeout=0)

            try:
                page.wait_for_selector('.user-image.user-image--icon.header-user-img', timeout=80_000)
            except:
                return False

            return True

    def validate_url_by_account(self, url: str, account) -> int:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()

            page.goto(url, timeout=0)

            page.wait_for_selector('.media-subscribe-and-notify', timeout=0)

            id = page.query_selector('.media-subscribe-and-notify').get_attribute('data-slug').replace('c-', '')

            page.goto('https://rumble.com/upload.php', timeout=0)

            page.wait_for_selector('#channelId')

            for option in page.query_selector('#channelId').query_selector_all('option'):
                if option.get_attribute('value') == id:
                    return True

            return False

    def need_to_pass_channel_after_login(self):
        return True
