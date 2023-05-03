import re
from abc import ABC
import abc
from playwright.sync_api import BrowserContext
from playwright.sync_api._context_manager import Playwright
from playwright.sync_api import Page
from yt_dlp import YoutubeDL
from PyQt5.QtWidgets import QTableWidgetItem
import time


class VideohostingService(ABC):

    __metaclass__ = abc.ABCMeta

    # Аргументы для выборки информации, используя yt-dlp
    extract_info_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'logger': False,
        "extract_flat": True,
    }

    # Аргументы для обхода защиты многих сайтов
    CHROMIUM_ARGS = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--no-first-run',
        '--disable-blink-features=AutomationControlled',
    ]

    downloading_videos = {}

    video_regex = None
    channel_regex = None

    @abc.abstractmethod
    def get_videos_by_url(self, url, account=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def show_login_dialog(self, hosting, form):
        raise NotImplementedError()

    @abc.abstractmethod
    def login(self, login, password):
        raise NotImplementedError()

    def new_context(self, p: Playwright, headless: bool) -> BrowserContext:
        browser = p.chromium.launch(headless=headless, args=self.CHROMIUM_ARGS)
        return browser.new_context()

    def download_video(self, url, account = None, table_item: QTableWidgetItem = None):
        #
        # download_opts = {
        #     'progress_hooks': [self.my_hook],
        # }

        with YoutubeDL() as ydl:
            # self.downloading_videos.__setattr__(url, table_item)
            ydl.download(url)

    # def my_hook(self, d, table_item):
    #     if d['status'] == 'finished':
    #         file_tuple = os.path.split(os.path.abspath(d['filename']))
    #         print("Done downloading {}".format(file_tuple[1]))
    #     if d['status'] == 'downloading':
    #         p = d['_percent_str']
    #         p = p.replace('%', '')
    #         self.progress.setValue(float(p))
    #         print(d['filename'], d['_percent_str'], d['_eta_str'])

    # Возвращает: 0, если ссылка невалидна; 1, если ссылка валидна и является ссылкой на канал;
    # 2, если ссылка валидна и является ссылкой на видео
    def validate_page(self, url: str) -> int:
        if re.match(self.video_regex, url):
            return 2
        elif re.match(self.channel_regex, url):
            return 1
        else:
            return 0

    def scroll_page_to_the_bottom(self, page: Page, timeout: int = 1):
        # для пагинации с использованием js-скриптов
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
                time.sleep(timeout)
            elif prev_height == curr_height:
                page.evaluate('clearInterval(intervalID)')
                break
            else:
                prev_height = curr_height
                time.sleep(timeout)
