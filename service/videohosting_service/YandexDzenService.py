import time
from datetime import datetime

from PyQt5.QtWidgets import QTableWidgetItem
from googletrans import Translator

from service.LocalizationService import get_str
from service.StateService import StateService
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from yt_dlp import YoutubeDL
from playwright.sync_api import sync_playwright


class YandexDzenService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/.*dzen.ru\/video\/watch\/.*'
        self.channel_regex = '(https:\/\/.*dzen.ru\/id\/.*)|(https:\/\/.*dzen.ru\/.*)'
        self.title_size_restriction = 200
        self.min_title_size = 0
        self.size_restriction = 30 * 1024
        self.duration_restriction = 240
        self.upload_video_formats = list(['3gpp', '3gp', 'x-fvl', 'mp4', 'webm', 'x-ms-wmv', 'x-ms-asf', 'ogg', 'mpeg',
                                          'quicktime', 'x-m4v', 'x-msvideo', 'mkv'])

    def get_videos_by_url(self, url: str, account=None):
        result = list()


        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            if account is not None:
                context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url, timeout=0)
            page.wait_for_selector('.card-video-ad-animations.card-video-2-view__content-wrap')
            self.scroll_page_to_the_bottom(page=page)

            elements = page.query_selector_all('.card-video-ad-animations.card-video-2-view__content-wrap')
            for box in elements:
                result.append(
                    VideoModel(url=box.query_selector('.zen-ui-line-clamp.zen-ui-card-title-clamp').get_attribute('href'),
                               name=box.query_selector('.zen-ui-line-clamp.zen-ui-card-title-clamp').text_content(),
                               date=box.query_selector('.zen-ui-common-layer-meta._type_card').text_content().split('•')[0]))

        return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(form, hosting, self, 1, get_str('login'), title=title, username_val=login, password_val=password, relogin=can_relogin)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://passport.yandex.ru/auth/welcome', timeout=0)
            page.keyboard.press('Enter')
            page.wait_for_selector('.Section_link__pZJDa', timeout=0)

            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False
    
    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            if table_item is not None:
                table_item.setText(get_str('preparing'))
            context = self.new_context(p=p, headless=StateService.settings.debug_browser is False, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://dzen.ru/profile/editor/create#video-editor', timeout=0)

            page.wait_for_selector('.author-studio-header__addButton-1Z.author-studio-header__rightItemButton-3a', timeout=0)
            page.click('.author-studio-header__addButton-1Z.author-studio-header__rightItemButton-3a')

            page.wait_for_selector('.ui-lib-context-menu__item.new-publication-dropdown__button-rl')
            page.query_selector_all('.ui-lib-context-menu__item.new-publication-dropdown__button-rl')[2].click()

            with page.expect_file_chooser() as fc_info:
                page.click('.base-button__rootElement-75.base-button__xl-28.base-button__accentPrimary-B4', timeout=0)
            if table_item is not None:
                table_item.setText(get_str('uploading'))
            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            if table_item is not None:
                table_item.setText(get_str('ending'))
            while True:
                try:
                    page.wait_for_selector('.ql-editor', timeout=3_000)
                    page.click('.ql-editor')
                    page.wait_for_selector('.ql-editor', timeout=3_000)
                    page.click('.ql-editor')
                    page.wait_for_selector('.ql-editor', timeout=3_000)
                    page.click('.ql-editor')
                    break
                except:
                    translator = Translator()
                    status = page.query_selector('.video-queue-drawer__item-error')

                    if status is not None and translator.translate(status.text_content()).text.strip() == 'Video in low resolution':
                        raise Exception('Видео в слишком низком разрешении')

            try:
                page.wait_for_selector('.Textarea-Control.Texteditor-Control.Texteditor-Control_withSizing.Texteditor-Control_withMargin', timeout=5_000)
                page.click('.Textarea-Control.Texteditor-Control.Texteditor-Control_withSizing.Texteditor-Control_withMargin', click_count=3)
                page.keyboard.press('Backspace')
                page.keyboard.type(text=name)

                time.sleep(1)

                page.click('.quill-text-field__editorContainer-mB.ql-container')
                page.keyboard.type(description)
            except:
                page.click('.quill-text-field__editorContainer-mB.ql-container', click_count=3)
                page.keyboard.press('Backspace')
                page.keyboard.type(name)

            page.click(
                '.form-actions__action-15.base-button__rootElement-75.base-button__l-3Z.base-button__accentPrimary-B4',
                timeout=0)

            time.sleep(5)

            if page.query_selector('.prepublish-popup-publisher-data__content') is not None:
                raise Exception('Необходимо активировать аккаунт')

    def check_auth(self, account) -> bool:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://dzen.ru/video', wait_until='domcontentloaded', timeout=0)
            try:
                page.wait_for_selector('.login-button__textButton-3Y', timeout=5_000)
                return False
            except:
                return True
