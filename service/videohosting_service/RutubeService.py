import time

from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from yt_dlp import YoutubeDL
from datetime import datetime
from playwright.sync_api import sync_playwright


class RutubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:/\/rutube.ru\/video\/.*'
        self.channel_regex = 'https:\/\/rutube.ru\/channel\/.*\/'
        self.upload_video_formats = list(['mp4', 'flv', 'avi', 'mov', 'mpg', 'wmv', 'm4v', 'mp3',
                                          'wma', '3gp', 'mkv', 'webm'])
        self.duration_restriction = 300
        self.size_restriction = 10 * 1024
        self.title_size_restriction = 100
        self.description_size_restriction = 5_000

    def get_videos_by_url(self, url: str, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            url = url if url.__contains__('videos') else url + 'videos'
            info = ydl.extract_info(url)
            for item in info['entries']:
                result.append(VideoModel(item['url'], item['title']
                                         , datetime.fromtimestamp(item['timestamp']).__str__()))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите название аккаунта')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://rutube.ru', timeout=0)
            page.wait_for_selector('.freyja_char-base-button__pointerCursor__JNA7y', timeout=0)
            page.click('.freyja_char-base-button__pointerCursor__JNA7y', timeout=0)
            page.wait_for_selector('.freyja_char-button__button__c4Dm-', timeout=0)
            page.click('.freyja_char-button__button__c4Dm-', timeout=0)

            page.wait_for_selector('.wdp-header-right-module__userWrapper', timeout=0)

            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False

    def upload_video(self, account, file_path, name, description, destination=None):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)

            page = context.new_page()
            page.goto('https://studio.rutube.ru/uploader/', timeout=0)

            with page.expect_file_chooser() as fc_info:
                page.click(
                    selector='.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__large__vS7yq.freyja_char-base-button__pointerCursor__JNA7y')
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            page.wait_for_selector('[name=title]', timeout=0)

            time.sleep(1)

            page.query_selector('[name="title"]').fill('')
            page.query_selector('[name="title"]').type(text=name)

            page.query_selector('[name="description"]').type(description if description is not None else '')

            page.click('[name="categories"]')
            page.click('.freyja_char-dropdown-layout__dropdownItem__x8JCK')

            page.wait_for_selector(
                '.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__regular__ksZLL.freyja_char-base-button__pointerCursor__JNA7y')

            page.click(
                selector='.freyja_char-base-button__button__7JyC-.freyja_char-base-button__contained-accent__Z8hc1.freyja_char-base-button__regular__ksZLL.freyja_char-base-button__pointerCursor__JNA7y',
                timeout=0)
