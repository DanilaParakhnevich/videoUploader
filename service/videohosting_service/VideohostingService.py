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
from service.videohosting_service.exception.NoFreeSpaceException import NoFreeSpaceException
from service.videohosting_service.exception.VideoDurationException import VideoDurationException
import os
import time


# Класс-родитель всех классов с основной логикой загрузки/выгрузки/авторизации
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

    user_agent_arg = '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"'

    # см метод validate_page
    video_regex = None
    channel_regex = None

    # Ограничения для выгрузки
    upload_video_formats = list()
    size_restriction = None  # в мегабайтах
    duration_restriction = None  # в минутах
    title_size_restriction = None
    description_size_restriction = None

    state_service = StateService()

    @abc.abstractmethod
    def get_videos_by_url(self, url, account=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def show_login_dialog(self, hosting, form):
        raise NotImplementedError()

    @abc.abstractmethod
    def login(self, login, password):
        raise NotImplementedError()

    def validate_video_info_for_uploading(self, video_dir=None, filesize=None, ext=None, duration=None, title=None, description=None):

        clip = None

        if video_dir is not None:
            clip = VideoFileClip(video_dir)

        # Получение размера в мегабайтах
        def get_size():
            file_size = os.path.getsize(video_dir)
            size = file_size / 1024 ** 2
            return round(size, 3)

        def validate_format(ext):
            if len(self.upload_video_formats) != 0:
                return self.upload_video_formats.__contains__(ext)

        if clip is not None:
            if self.duration_restriction is not None and (clip.duration / 60) > self.duration_restriction:
                raise VideoDurationException(f'Продолжительность ролика слишком большая ({clip.duration} > {self.duration_restriction})')

            size = get_size()
            if self.size_restriction is not None and size is not None and size > self.size_restriction:
                raise FileSizeException(f'Размер файла слишком большой ({size} > {self.size_restriction})')

            if validate_format(os.path.splitext(video_dir)[1].replace('.', '')) is False:
                raise FileFormatException(f'Неподходящий формат для видеохостинга({clip.filename} не подходит к {self.upload_video_formats.__str__()})')

        if self.duration_restriction is not None and duration is not None and (duration / 60) > self.duration_restriction:
            raise VideoDurationException(
                f'Продолжительность ролика слишком большая ({duration} > {self.duration_restriction})')

        if self.size_restriction is not None and filesize is not None and filesize > self.size_restriction:
            raise FileSizeException(f'Размер файла слишком большой ({filesize} > {self.size_restriction})')

        if ext is not None and validate_format(ext) is False:
            raise FileFormatException(
                f'Неподходящий формат для видеохостинга({ext} не подходит к {self.upload_video_formats.__str__()})')

        if self.title_size_restriction is not None and title is not None and len(title) > self.title_size_restriction:
            raise NameIsTooLongException(f'Слишком большой размер названия(Ограничение: {self.title_size_restriction} символов)')

        if self.description_size_restriction is not None and description is not None and len(description) > self.description_size_restriction:
            raise DescriptionIsTooLongException(f'Слишком большой размер описания(Ограничение {self.description_size_restriction} символов)')

    def upload_video(self, account, file_path, name, description, destination=None):
        raise NotImplementedError()

    def new_context(self, p: Playwright, headless: bool, use_user_agent_arg: bool = False) -> BrowserContext:

        args = self.CHROMIUM_ARGS.copy()

        if use_user_agent_arg:
            args.append(self.user_agent_arg)

        browser = p.chromium.launch(headless=headless, args=args)
        return browser.new_context()

    def download_video(self, url, hosting, video_quality, format, download_dir, account=None, table_item: QTableWidgetItem = None):

        from model.Hosting import Hosting
        video_info = Hosting[hosting].value[0].get_video_info(url, video_quality)

        space = os.statvfs(os.path.expanduser(download_dir))
        free = space.f_bavail * space.f_frsize / 1024000

        if free - video_info['filesize'] < 100:
            raise NoFreeSpaceException(f'Нет свободного места: размер файла: {video_info["filesize"]}')

        def prog_hook(d, table_item):
            if d["status"] == "downloading":
                if d['total_bytes_estimate'] != 0:
                    p = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                    table_item.setText(str(round(p, 1)) + '%')
                else:
                    table_item.setText(d['_percent_str'])

        settings = self.state_service.get_settings()

        simple_download_opts = {
            'progress_hooks': [lambda d: prog_hook(d, table_item)],
            'ffmpeg_location': os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/bin'),
            'outtmpl': f'{download_dir}/{hosting}/%(title)s.%(ext)s',
            'writeinfojson': True,
            '--retries': settings.retries,
            '--no-check-certificate': settings.no_check_certificate,
            '--audio-quality': settings.audio_quality,
            '--no-cache-dir': settings.no_cache_dir
        }

        if settings.referer != '':
            simple_download_opts['--referer'] = settings.referer

        # Чтобы нормально добавить куки в обычном json, приходится использовать http_headers
        if account is not None and isinstance(account.auth, list):
            cookie_str = ''
            for auth in account.auth:
                cookie_str += f'{auth["name"]}={auth["value"]}; '
            simple_download_opts["http_headers"] = {"Set-Cookie": cookie_str}

        if StateService.settings.rate_limit != 0:
            simple_download_opts['ratelimit'] = str(StateService.settings.rate_limit * 1024)

        if format == 'NOT_MERGE':
            download_video_opts = {
                'ffmpeg_location': os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/bin'),
                'format': f'bestvideo[height<={video_quality}]/best[height<={video_quality}]/best',
                '--list-formats ': True,
                'outtmpl': f'{download_dir}/{hosting}/%(title)s.%(ext)s',
                'writeinfojson': True,
                '--retries': settings.retries,
                '--no-check-certificate': settings.no_check_certificate,
                '--audio-quality': settings.audio_quality,
                '--no-cache-dir': settings.no_cache_dir
            }

            download_audio_opts = {
                'ffmpeg_location': os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/bin'),
                'format': 'bestaudio/best',
                '--list-formats ': True,
                'outtmpl': f'{download_dir}/{hosting}/audio_%(title)s.%(ext)s',
                '--retries': settings.retries,
                '--no-check-certificate': settings.no_check_certificate,
                '--audio-quality': settings.audio_quality,
                '--no-cache-dir': settings.no_cache_dir
            }

            if settings.referer != '':
                download_audio_opts['--referer'] = settings.referer
                download_video_opts['--referer'] = settings.referer

            if 'http_headers' in simple_download_opts.keys():
                download_audio_opts['http_headers'] = simple_download_opts['http_headers']
                download_video_opts['http_headers'] = simple_download_opts['http_headers']
            if 'ratelimit' in simple_download_opts.keys():
                download_audio_opts['ratelimit'] = simple_download_opts['ratelimit']
                download_video_opts['ratelimit'] = simple_download_opts['ratelimit']

            with YoutubeDL(download_video_opts) as ydl:
                info = ydl.extract_info(url)

            with YoutubeDL(download_audio_opts) as ydl:
                ydl.extract_info(url)

        else:

            if format == 'AUDIO':
                simple_download_opts['format'] = 'bestaudio/best'
            elif format == 'VIDEO':
                simple_download_opts['format'] = f'bestvideo[height<={video_quality}]/best[height<={video_quality}]/best'
            else:
                simple_download_opts['format'] = f'bestvideo[height<={video_quality}]+bestaudio/best[height<={video_quality}]/best'

            with YoutubeDL(simple_download_opts) as ydl:
                info = ydl.extract_info(url)

        if 'video_ext' in info:
            return f'{download_dir}/{hosting}/{info["title"]}.{info["video_ext"]}'
        else:
            return f'{download_dir}/{hosting}/{info["title"]}.{info["ext"]}'

    def get_video_info(self, url, video_quality, account=None):

        download_opts = {
            'skip_download': True,
            'format': f'bestvideo[height<={video_quality}]+bestaudio/best[height<={video_quality}]/best'
        }

        # Чтобы нормально добавить куки в обычном json, приходится использовать http_headers
        if account is not None and isinstance(account.auth, list):
            cookie_str = ''
            for auth in account.auth:
                cookie_str += f'{auth["name"]}={auth["value"]}; '
            download_opts["http_headers"] = {"Set-Cookie": cookie_str}

        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(url)

        return {
            'title': info['title'],
            'description': info['description'] if hasattr(info, 'description') else '',
            'duration': info['duration'],
            'filesize': int(info['filesize_approx'] / 1024 ** 2) if 'filesize_approx' in info else int(info['filesize'] / 1024 ** 2),
            'ext': info['ext'] if info['ext'] else info['video_ext']
        }

    # Возвращает: False, если ссылка не является ссылкой на канал аккаунта, True, если является
    def validate_url_by_account(self, url: str, account) -> int:
        pass

    def need_to_pass_channel_after_login(self):
        return True

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

    def is_async(self) -> bool:
        return False
