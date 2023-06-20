import time

from PyQt5.QtWidgets import QTableWidgetItem

from service.LocalizationService import get_str
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import scrapetube


class YoutubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.youtube.com\/watch\?v=.*'
        self.channel_regex = '(https:\/\/www.youtube.com\/@.*)|(https:\/\/www.youtube.com\/channel\/)'
        self.title_size_restriction = 100
        self.min_title_size = 1
        self.description_size_restriction = 5_000
        self.size_restriction = 256 * 1024
        self.duration_restriction = 12 * 60
        self.upload_video_formats = list(['mov', 'mpeg-1', 'mpeg-2', 'mp4', 'mpg', 'avi', 'wmv', 'mpegps',
                                          'flv', '3gpp', 'webm', 'DNxHR', 'ProRes', 'CineForm', 'hevc', 'mkv'])

    def get_videos_by_url(self, url, account=None):
        c = scrapetube.get_channel(channel_url=url)
        result = list()
        for video in c:
            url = f'https://www.youtube.com/{video["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]}'
            if 'simpleText' in video['title'].keys():
                title = video['title']['simpleText']
            else:
                title = video['title']['runs'][0]['text']
            result.append(VideoModel(url, title, video['publishedTimeText']['simpleText']))
        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите телефон или адрес эл. почты')
        self.login_form.exec_()
        return self.login_form.account
    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False, use_user_agent_arg=True)
            page = context.new_page()
            page.goto('https://accounts.google.com/signin', timeout=0)
            page.wait_for_selector('.XY0ASe', timeout=0)

            return page.context.cookies()

    def validate_url_by_account(self, url: str, account) -> int:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()

            page.goto(url)

            channel_id = None

            for channel_handle in page.query_selector_all('#channel-handle'):
                if channel_handle is not None:
                    channel_id = channel_handle.text_content()
                    break

            page.goto('https://www.youtube.com/channel_switcher?next=%2Faccount&feature=settings', timeout=0)

            page.wait_for_url('https://www.youtube.com/account', timeout=0)
            page.wait_for_selector('.ytd-account-item-renderer', timeout=0)

            for title_element in page.query_selector_all('.ytd-account-item-renderer'):
                if channel_id is not None and title_element.text_content() == channel_id:
                    return True
            return False

    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            table_item.setText(get_str('preparing'))
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()

            page.goto(destination, timeout=0)

            for channel_handle in page.query_selector_all('#channel-handle'):
                if channel_handle is not None:
                    channel_id = channel_handle.text_content()
                    break

            page.goto('https://www.youtube.com/channel_switcher?next=%2Faccount&feature=settings', timeout=0)

            page.wait_for_url('https://www.youtube.com/account', timeout=0)
            page.wait_for_selector('.ytd-account-item-renderer', timeout=0)

            for title_element in page.query_selector_all('.ytd-account-item-renderer'):
                if title_element.text_content() == channel_id:
                    title_element.click()
                    break

            page.goto('https://www.youtube.com/', timeout=0)

            page.wait_for_selector('.yt-simple-endpoint.style-scope.ytd-topbar-menu-button-renderer',
                                   timeout=0).click()
            page.query_selector_all('.yt-simple-endpoint.style-scope.ytd-compact-link-renderer')[0].click(timeout=0)

            page.wait_for_selector('#select-files-button', timeout=0)
            with page.expect_file_chooser() as fc_info:
                page.query_selector(selector='#select-files-button').click()

            table_item.setText(get_str('uploading'))
            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            table_item.setText(get_str('ending'))
            page.wait_for_selector('#input', timeout=0)

            page.query_selector('#title-textarea').click(click_count=3)
            page.keyboard.press("Backspace")
            page.query_selector('#title-textarea').type(text=name)

            page.query_selector('#description-textarea').click()
            page.query_selector('#description-textarea').type(text=description if description is not None else '')

            page.click(selector='#next-button', timeout=0)

            page.click(selector='[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]', timeout=0)

            page.click(selector='#next-button', timeout=0)
            page.click(selector='#next-button', timeout=0)
            page.click(selector='#next-button', timeout=0)

            page.click(selector='[name=PUBLIC]', timeout=0)

            page.click(selector='#done-button', timeout=0)

            time.sleep(1)

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True
