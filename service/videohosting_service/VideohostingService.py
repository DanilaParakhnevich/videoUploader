import re
import traceback
from abc import ABC
import abc
from playwright.sync_api import BrowserContext
from playwright.sync_api import Playwright
from playwright.sync_api import Page
from PyQt5.QtWidgets import QTableWidgetItem
from moviepy.editor import VideoFileClip

from service.LocalizationService import get_str
from service.LoggingService import log_error
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
    min_title_size = None
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

    def validate_video_info_for_uploading(self, video_dir=None, filesize=None, ext=None, duration=None, title=None,
                                          description=None):

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
                raise VideoDurationException(
                    f'Продолжительность ролика слишком большая ({clip.duration / 60} > {self.duration_restriction})')

            size = get_size()
            if self.size_restriction is not None and size is not None and size > self.size_restriction:
                raise FileSizeException(f'Размер файла слишком большой ({size} > {self.size_restriction})')

            if validate_format(os.path.splitext(video_dir)[1].replace('.', '')) is False:
                raise FileFormatException(
                    f'Неподходящий формат для видеохостинга({clip.filename} не подходит к {self.upload_video_formats.__str__()})')

        if self.duration_restriction is not None and duration is not None and (
                duration / 60) > self.duration_restriction:
            raise VideoDurationException(
                f'Продолжительность ролика слишком большая ({duration} > {self.duration_restriction})')

        if self.size_restriction is not None and filesize is not None and filesize is int and filesize > self.size_restriction:
            raise FileSizeException(f'Размер файла слишком большой ({filesize} > {self.size_restriction})')

        if ext is not None and validate_format(ext) is False:
            raise FileFormatException(
                f'Неподходящий формат для видеохостинга({ext} не подходит к {self.upload_video_formats.__str__()})')

        if self.title_size_restriction is not None and title is not None and len(title) > self.title_size_restriction:
            raise NameIsTooLongException(
                f'Слишком большой размер названия(Ограничение: {self.title_size_restriction} символов)')

        if self.min_title_size is not None and title is not None and len(title) < self.min_title_size:
            raise NameIsTooLongException(
                f'Слишком маленький размер названия(Ограничение: {self.min_title_size} символов)')

        if self.description_size_restriction is not None and description is not None and len(
                description) > self.description_size_restriction:
            raise DescriptionIsTooLongException(
                f'Слишком большой размер описания(Ограничение {self.description_size_restriction} символов)')

    def upload_video(self, account, file_path, name, description, destination=None,
                     table_item: QTableWidgetItem = None):
        raise NotImplementedError()

    def new_context(self, p: Playwright, headless: bool, use_user_agent_arg: bool = False) -> BrowserContext:

        args = self.CHROMIUM_ARGS.copy()

        if use_user_agent_arg:
            args.append(self.user_agent_arg)

        browser = p.chromium.launch(headless=headless, args=args)
        return browser.new_context()

    def download_video(self, url, hosting, manual_settings, video_quality_str, audio_quality_str, video_bitrate,
                       audio_bitrate, audio_sampling_rate, fps, video_quality, video_extension, format, download_dir,
                       account=None, table_item: QTableWidgetItem = None):

        from model.Hosting import Hosting
        video_info = Hosting[hosting].value[0].get_video_info(url, video_quality=video_quality,
                                                              video_extension=video_extension,
                                                              video_quality_str=video_quality_str,
                                                              fps=fps,
                                                              audio_quality_str=audio_quality_str,
                                                              audio_bitrate=audio_bitrate,
                                                              video_bitrate=video_bitrate,
                                                              audio_sampling_rate=audio_sampling_rate,
                                                              manual_settings=manual_settings)

        if hosting == 'Facebook':
            from youtube_dl import YoutubeDL
        else:
            from yt_dlp import YoutubeDL

        space = os.statvfs(os.path.expanduser(download_dir))
        free = space.f_bavail * space.f_frsize / 1024000

        if video_info['filesize'] is int and free - video_info['filesize'] < 100:
            raise NoFreeSpaceException(f'Нет свободного места: размер файла: {video_info["filesize"]}')

        download_path = fr'{download_dir}/{hosting}/%(title)s_{video_quality}.%(ext)s' if manual_settings \
            else fr'{download_dir}/{hosting}/%(title)s.%(ext)s'

        download_audio_path = fr'{download_dir}/{hosting}/audio_%(title)s_{video_quality}.%(ext)s' if manual_settings \
            else fr'{download_dir}/{hosting}/audio_%(title)s.%(ext)s'

        def prog_hook(d, table_item):
            try:
                if d["status"] == "downloading":
                    str = 'total_bytes' if 'total_bytes' in d else 'total_bytes_estimate'
                    if d[str] != 0:
                        p = (d['downloaded_bytes'] / d[str]) * 100
                        if video_info['filesize'] is int:
                            table_item.setText(f'{round(p, 1).__str__()}% ({video_info["filesize"]} MB)')
                        else:
                            table_item.setText(f'{round(p, 1).__str__()}%')
                    else:
                        if video_info['filesize'] is int:
                            table_item.setText(f'{d["_percent_str"]} ({video_info["filesize"]} MB)')
                        else:
                            table_item.setText(f'{d["_percent_str"]}')
            except:
                log_error(traceback.format_exc())

        settings = self.state_service.get_settings()

        ffmpeg_location = f'{settings.ffmpeg}/bin/ffmpeg'

        simple_download_opts = {
            'progress_hooks': [lambda d: prog_hook(d, table_item)],
            'ffmpeg_location': ffmpeg_location,
            'outtmpl': download_path,
            'writeinfojson': True,
            'retries': settings.retries,
            'nocheckcertificate': settings.no_check_certificate,
            '--audio-quality': settings.audio_quality,
            'cachedir': settings.no_cache_dir is False,
            'keepvideo': settings.keep_fragments,
            'buffersize': settings.buffer_size,
            'writesubtitles': settings.write_sub,
            'overwrites': True
        }

        if settings.embed_subs and hosting != 'Facebook':
            simple_download_opts['postprocessors'] = [{'already_have_subtitle': False, 'key': 'FFmpegEmbedSubtitle'}]

        if settings.referer != '':
            simple_download_opts['--referer'] = settings.referer

        if settings.geo_bypass_country != '':
            simple_download_opts['--geo-bypass-country'] = settings.geo_bypass_country

        # Чтобы нормально добавить куки в обычном json, приходится использовать http_headers
        if account is not None and isinstance(account.auth, list):
            cookie_str = ''
            for auth in account.auth:
                cookie_str += f'{auth["name"]}={auth["value"]}; '
            simple_download_opts["http_headers"] = {"Set-Cookie": cookie_str}

        if StateService.settings.rate_limit != 0:
            simple_download_opts['ratelimit'] = str(StateService.settings.rate_limit * 1024)

        video_format_str = f'[height={video_quality}]'
        audio_format_str = ''
        if manual_settings:
            if audio_bitrate != '0':
                audio_format_str += f'[abr<=?{audio_bitrate}]'
            if video_bitrate != '0':
                video_format_str += f'[vbr<=?{video_bitrate}]'
            if audio_sampling_rate != '0':
                audio_format_str += f'[asr<=?{audio_sampling_rate}]'
            if fps != '0':
                video_format_str += f'[fps<=?{fps}]'

        if format == 'NOT_MERGE':

            if manual_settings:
                video_format = f'bestvideo[ext={video_extension}]{video_format_str}/bestvideo[ext=?{video_extension}]{video_format_str}/best[ext=?{video_extension}]{video_format_str}/best[ext=?{video_extension}]/best'
            else:
                if video_quality_str == 0:
                    video_format = 'bestvideo'
                else:
                    video_format = 'worstvideo'

            download_video_opts = {
                'ffmpeg_location': ffmpeg_location,
                'format': video_format,
                '--list-formats ': True,
                'outtmpl': download_path,
                'writeinfojson': True,
                'retries': settings.retries,
                'nocheckcertificate': settings.no_check_certificate,
                '--audio-quality': settings.audio_quality,
                'cachedir': settings.no_cache_dir is False,
                'keepvideo': settings.keep_fragments,
                'buffersize': settings.buffer_size,
                'writesubtitles': settings.write_sub,
                'overwrites': True
            }

            if manual_settings:
                audio_format = f'bestaudio{audio_format_str}/bestaudio{audio_format_str}/best{audio_format_str}/best'
            else:
                if video_quality_str == 0:
                    audio_format = 'bestaudio'
                else:
                    audio_format = 'worstaudio'

            download_audio_opts = {
                'ffmpeg_location': ffmpeg_location,
                'format': audio_format,
                '--list-formats ': True,
                'outtmpl': download_audio_path,
                'retries': settings.retries,
                'nocheckcertificate': settings.no_check_certificate,
                '--audio-quality': settings.audio_quality,
                'cachedir': settings.no_cache_dir is False,
                'keepvideo': settings.keep_fragments,
                'buffersize': settings.buffer_size,
                'writesubtitles': settings.write_sub,
                'overwrites': True
            }

            if settings.referer != '':
                download_audio_opts['--referer'] = settings.referer
                download_video_opts['--referer'] = settings.referer

            if settings.geo_bypass_country != '':
                download_audio_opts['--geo-bypass-country'] = settings.geo_bypass_country
                download_video_opts['--geo-bypass-country'] = settings.geo_bypass_country
            if 'postprocessors' in simple_download_opts.keys():
                download_audio_opts['postprocessors'] = simple_download_opts['postprocessors']
                download_video_opts['postprocessors'] = simple_download_opts['postprocessors']
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
                if manual_settings:
                    audio_format = f'bestaudio{audio_format_str}/best'
                else:
                    if video_quality_str == 0:
                        audio_format = 'bestaudio'
                    else:
                        audio_format = 'worstaudio'

                simple_download_opts['outtmpl'] = download_audio_path
                simple_download_opts['format'] = audio_format
            elif format == 'VIDEO':
                if manual_settings:
                    video_format = f'bestvideo[ext={video_extension}]{video_format_str}/bestvideo[ext=?{video_extension}]{video_format_str}/best[ext=?{video_extension}]{video_format_str}/best[ext=?{video_extension}]/best'
                else:
                    if video_quality_str == 0:
                        video_format = 'bestvideo'
                    else:
                        video_format = 'worstvideo'
                simple_download_opts['format'] = video_format
            else:
                if manual_settings:
                    video_format = f'bestvideo[ext={video_extension}]{video_format_str}+bestaudio{audio_format_str}/bestvideo[ext=?{video_extension}]{video_format_str}+bestaudio/best[ext=?{video_extension}]{video_format_str}+bestaudio/best[ext=?{video_extension}]/best'
                else:
                    audio_format = 'bestaudio' if audio_quality_str == 0 else 'worstaudio'
                    if video_quality_str == 0:
                        video_format = f'bestvideo+{audio_format}'
                    else:
                        video_format = f'worstvideo+{audio_format}'
                simple_download_opts['format'] = video_format
                simple_download_opts['merge_output_format'] = video_extension

            with YoutubeDL(simple_download_opts) as ydl:
                info = ydl.extract_info(url)

        if 'title' in info:
            title = info['title']
            ext = info['ext'] if 'ext' in info and info['ext'] is not None else info['video_ext']
        else:
            title = info['entries'][0]['title']
            ext = info['entries'][0]['ext']

        title = title.replace('/', '|')
        if manual_settings:
            if 'video_ext' in info:
                return f'{download_dir}/{hosting}/{title}_{video_quality}.{ext}'
            else:
                return f'{download_dir}/{hosting}/{title}_{video_quality}.{ext}'
        else:
            if 'video_ext' in info:
                return f'{download_dir}/{hosting}/{title}.{ext}'
            else:
                return f'{download_dir}/{hosting}/{title}.{ext}'

    def get_video_info(self, url: str, manual_settings, video_quality_str, audio_quality_str, video_bitrate,
                       audio_bitrate, audio_sampling_rate, fps, video_quality, video_extension, account=None):

        if url.__contains__('Facebook'):
            from youtube_dl import YoutubeDL
        else:
            from yt_dlp import YoutubeDL

        if manual_settings:
            video_format_str = f'[height={video_quality}]'
            audio_format_str = ''
            if manual_settings:
                if audio_bitrate != '0':
                    audio_format_str += f'[abr<=?{audio_bitrate}]'
                if video_bitrate != '0':
                    video_format_str += f'[vbr<=?{video_bitrate}]'
                if audio_sampling_rate != '0':
                    audio_format_str += f'[asr<=?{audio_sampling_rate}]'
                if fps != '0':
                    video_format_str += f'[fps<=?{fps}]'

            video_format = f'bestvideo[ext={video_extension}]{video_format_str}+bestaudio{audio_format_str}/bestvideo[ext=?{video_extension}]{video_format_str}+bestaudio/best[ext=?{video_extension}]{video_format_str}+bestaudio/best[ext=?{video_extension}]/best'
        else:
            audio_format = 'bestaudio' if audio_quality_str == 0 else 'worstaudio'
            if video_quality_str == 0:
                video_format = f'bestvideo+{audio_format}'
            else:
                video_format = f'worstvideo+{audio_format}'

        download_opts = {
            'skip_download': True,
            'format': video_format,
            'merge_output_format': video_extension
        }

        # Чтобы нормально добавить куки в обычном json, приходится использовать http_headers
        if account is not None and isinstance(account.auth, list):
            cookie_str = ''
            for auth in account.auth:
                cookie_str += f'{auth["name"]}={auth["value"]}; '
            download_opts["http_headers"] = {"Set-Cookie": cookie_str}

        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(url)
        filesize = get_str('no_info')
        if 'filesize' in info and info['filesize'] is not None:
            filesize = int(info['filesize'] / 1024 ** 2)
        elif 'filesize_approx' in info:
            filesize = int(info['filesize_approx'] / 1024 ** 2)

        is_exists_format = None
        saved_video_height = None

        for format in info['formats']:

            extracted_video_ext = None

            if 'video_ext' in format:
                extracted_video_ext = format['video_ext']
            elif 'ext' in format:
                extracted_video_ext = format['ext']

            extracted_video_height = None

            if 'height' in format:
                extracted_video_height = format['height']

            if video_extension == extracted_video_ext and int(video_quality.replace('p', '')) == extracted_video_height:
                is_exists_format = [True, saved_video_height]
                break
            elif video_extension == extracted_video_ext:
                if extracted_video_ext is not None and (
                        saved_video_height is None or extracted_video_ext <= video_quality):
                    saved_video_height = extracted_video_height

        if is_exists_format is None:
            is_exists_format = [False, saved_video_height]

        return {
            'title': info['title'],
            'description': info['description'] if hasattr(info, 'description') else '',
            'duration': info['duration'],
            'filesize': filesize,
            'ext': info['ext'] if info['ext'] else info['video_ext'],
            'is_exists_format': is_exists_format
        }

    def check_auth(self, account) -> bool:
        pass

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
