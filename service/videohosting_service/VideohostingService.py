import re
from abc import ABC
import abc
from playwright.sync_api import BrowserContext
from playwright.sync_api import Playwright
from playwright.sync_api import Page
from yt_dlp import YoutubeDL
from PyQt5.QtWidgets import QTableWidgetItem
from moviepy.editor import VideoFileClip
from service.StateService import StateService
from service.videohosting_service.exception.DescriptionIsTooLongException import DescriptionIsTooLongException
from service.videohosting_service.exception.FileFormatException import FileFormatException
from service.videohosting_service.exception.FileSizeException import FileSizeException
from service.videohosting_service.exception.NameIsTooLongException import NameIsTooLongException
from service.videohosting_service.exception.VideoDurationException import VideoDurationException
import os
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

    # Ограничения для выгрузки
    upload_video_formats = list()
    size_restriction = None  # в мегабайтах
    duration_restriction = None  # в минутах
    name_size_restriction = None
    description_size_restriction = None

    @abc.abstractmethod
    def get_videos_by_url(self, url, account=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def show_login_dialog(self, hosting, form):
        raise NotImplementedError()

    @abc.abstractmethod
    def login(self, login, password):
        raise NotImplementedError()

    def validate_video_info_for_uploading(self, video_dir, name, description):
        clip = VideoFileClip(video_dir)

        # Получение размера в мегабайтах
        def get_size():
            file_size = os.path.getsize(video_dir)
            size = file_size / 1024 ** 2
            return round(size, 3)

        def validate_format():
            return self.upload_video_formats.__contains__(os.path.splitext(video_dir)[1])

        if (clip.duration / 60) > self.duration_restriction:
            raise VideoDurationException(f'Продолжительность ролика слишком большая ({clip.duration} > {self.duration_restriction})')

        size = get_size()
        if size > self.size_restriction:
            raise FileSizeException(f'Размер файла слишком большой ({size} > {self.size_restriction})')

        if validate_format() is False:
            raise FileFormatException(f'Неподходящий формат для видеохостинга({clip.filename} не подходит к {self.upload_video_formats.__str__()})')

        if self.name_size_restriction is not None and size(name) > self.name_size_restriction:
            raise NameIsTooLongException(f'Слишком большой размер названия(Ограничение: {self.name_size_restriction} символов)')

        if self.description_size_restriction is not None and size(description) > self.description_size_restriction:
            raise DescriptionIsTooLongException(f'Слишком большой размер описания(Ограничение {self.description_size_restriction} символов)')

    def upload_video(self, account, file_path, name, description):
        raise NotImplementedError()

    def new_context(self, p: Playwright, headless: bool) -> BrowserContext:
        browser = p.chromium.launch(headless=headless, args=self.CHROMIUM_ARGS)
        return browser.new_context()

    def download_video(self, url, hosting, account=None, table_item: QTableWidgetItem = None):

        def prog_hook(d, table_item):
            if d["status"] == "downloading":
                p = d['_percent_str']
                table_item.setText(p)

        download_opts = {
            'progress_hooks': [lambda d: prog_hook(d, table_item)],
            'ffmpeg_location': os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/bin'),
            'outtmpl': f'{StateService.settings.download_dir}/{hosting}/%(title)s.%(ext)s',
            'writeinfojson': True
        }

        if account is not None and isinstance(account.auth, list):
            cookie_str = ''
            for auth in account.auth:
                cookie_str += f'{auth["name"]}={auth["value"]}; '
            download_opts["http_headers"] = {"Set-Cookie": cookie_str}

        if StateService.settings.rate_limit != 0:
            download_opts['ratelimit'] = str(StateService.settings.rate_limit * 1024)

        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(url)
            if 'video_ext' in info:
                return f'{StateService.settings.download_dir}/{hosting}/{info["title"]}.{info["video_ext"]}'
            else:
                return f'{StateService.settings.download_dir}/{hosting}/{info["title"]}.{info["ext"]}'

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

    # Методы для определения конечного источника выгрузки видео для некоторых видеохостингов
    def need_to_be_uploaded_to_special_source(self) -> bool:
        return False  # False - видеохостингу не нужна эта логика

    def validate_special_source(self, account, source_name) -> bool:
        raise NotImplementedError()
