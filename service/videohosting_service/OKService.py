import time

from PyQt5.QtWidgets import QTableWidgetItem

from service.LocalizationService import get_str
from service.StateService import StateService
from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
from gui.widgets.LoginForm import LoginForm
from model.VideoModel import VideoModel
import sys


class OKService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https://.*ok.ru/video/.*'
        self.channel_regex = 'https:\/\/.*ok.ru\/.*'
        self.duration_restriction = sys.maxsize
        self.size_restriction = 2 * 1024
        self.min_title_size = 1
        self.upload_video_formats = list(['avi', 'mp4', '3gp', 'mpeg', 'mov', 'flv', 'f4v', 'wmv', 'mkv', 'webm', 'vob',
                                          'rmvb', 'm4v', 'mpg', 'ogv', 'ts', 'm2ts', 'mts', 'mxf', 'torrent'])
        self.title_size_restriction = 9_999_999_999
        self.description_size_restriction = 9_999_999_999

    def get_videos_by_url(self, url: str, account=None):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            page.goto(url, timeout=0)
            if url.__contains__('group'):
                page.click('a[data-l="outlandermenu,altGroupVideoAll"]', timeout=60_000)
            elif url.__contains__('feed'):
                page.click('[href*="/video/showcase"]', timeout=60_000)
                page.click('#mctc_navMenuDropdownSec_vv-myVideo')
            else:
                page.click('a[data-l="outlandermenu,userFriendVideoNew"]', timeout=60_000)

            try:
                page.wait_for_selector('.ugrid.ugrid__video', timeout=60_000)
            except:
                return list()

            self.scroll_page_to_the_bottom(page=page)

            result = list()
            stream_boxes = page.locator("//a[contains(@class,'video-card_n')]")

            for box in stream_boxes.element_handles():
                if str(box.get_property('href')).__contains__('video'):
                    result.append(
                        VideoModel(url=str(box.get_property('href')), name=box.inner_html(), date=get_str('no_info')))

        return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(form, hosting, self, 2, get_str('enter_login'), get_str('enter_pas'), title=title, username_val=login, password_val=password, relogin=can_relogin)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://ok.ru/', timeout=0)
            page.type('#field_email', login)
            page.type('#field_password', password)
            page.keyboard.press('Enter')
            page.wait_for_selector('.html5-upload-link', timeout=0)
            return page.context.cookies()

    def validate_url_by_account(self, url: str, account) -> int:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://ok.ru/', timeout=0)
            page.goto(url, timeout=0)

            page.wait_for_selector('.portlet_h')
            user_item = page.query_selector('.u-menu.__items-count-2.header-action-menu.__v4.__small.__user')
            group_item = page.query_selector('.ugrid_i.__invite_friends.group-onboarding_i')

            if user_item is None and group_item is None:
                return False
            else:
                return True

    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            if table_item is not None:
                table_item.setText(get_str('preparing'))
            context = self.new_context(p=p, headless=StateService.settings.debug_browser is False)
            context.add_cookies(account.auth)
            page = context.new_page()

            page.goto('https://ok.ru/', timeout=0)
            page.goto(destination, timeout=0)

            page.wait_for_selector('.portlet_h', timeout=0)
            user_item = page.query_selector('.u-menu.__items-count-2.header-action-menu.__v4.__small.__user')

            if user_item is not None:
                page.goto('https://ok.ru/video/manager', timeout=0)
            else:
                page.goto(destination + '/video/manager', timeout=0)

            page.wait_for_selector('.button-pro.js-upload-button', timeout=0)

            with page.expect_file_chooser() as fc_info:
                page.click(selector='.button-pro.js-upload-button')
            if table_item is not None:
                table_item.setText(get_str('uploading'))
            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            if table_item is not None:
                table_item.setText(get_str('ending'))
            page.wait_for_selector('.__small.video-uploader_ac.__go-to-editor-btn.js-uploader-editor-link', timeout=0)
            page.click('.__small.video-uploader_ac.__go-to-editor-btn.js-uploader-editor-link', timeout=0)

            page.wait_for_selector('#movie-title', timeout=0)

            page.query_selector('#movie-title').click(click_count=3)
            page.keyboard.press('Backspace')
            page.keyboard.type(text=name)

            page.wait_for_selector('#movie-description')

            page.query_selector('#movie-description').click()
            page.keyboard.type(text=description if description is not None else '')

            page.click('.button-pro.js-submit-annotations-form', timeout=0)

            time.sleep(0.5)

    def check_auth(self, account) -> bool:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://ok.ru/', wait_until='domcontentloaded', timeout=0)

            return page.query_selector('.anonym_login_design21') is None

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True
