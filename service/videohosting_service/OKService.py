import time

from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
from gui.widgets.LoginForm import LoginForm
from model.VideoModel import VideoModel


class OKService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https://ok.ru/video/.*'
        self.channel_regex = 'https:\/\/ok.ru\/.*\/video'

    def get_videos_by_url(self, url, account=None):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url)
            page.wait_for_selector('#listBlockPanelAltGroupVideoMoviesPagingBlock')

            self.scroll_page_to_the_bottom(page=page)

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
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://ok.ru/')
            page.type('#field_email', login)
            page.type('#field_password', password)
            page.keyboard.press('Enter')
            page.wait_for_selector('.html5-upload-link', timeout=0)
            return page.context.cookies()

    def upload_video(self, account, file_path, name, description):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://ok.ru/video/showcase')

            page.click('.svg-ico_video_add_16')

            with page.expect_file_chooser() as fc_info:
                page.click(selector='.button-pro.js-upload-button')
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            page.click('.__small.video-uploader_ac.__go-to-editor-btn.js-uploader-editor-link', timeout=60_000)

            time.sleep(0.5)

            page.query_selector('#movie-title').fill('')
            page.query_selector('#movie-title').type(text=name)

            page.query_selector('#movie-description').type(text=description)

            page.click('.button-pro.js-submit-annotations-form', timeout=0)

            time.sleep(0.5)
