class Settings(object):

    def __init__(self, language: str, download_strategy: int, rate_limit: int,
                 download_dir: str, pack_count: int = 0, send_crash_notifications: bool = True,
                 video_quality=0, video_extension=5, format=0, save_password=True, remove_files_after_upload=False, autostart: bool = False,
                 retries=10, no_check_certificate=False, audio_quality=9, no_cache_dir=False, referer='',
                 geo_bypass_country='', keep_fragments=False, buffer_size=1024, write_sub=False, embed_subs=False,
                 manual_settings: bool = False, audio_bitrate = 0, video_bitrate = 0, audio_sampling_rate = 0, fps = 0,
                 video_quality_str=0, audio_quality_str=0, encrypted_key=None, user_mail=None, ffmpeg=None, debug_browser=False, enable_autostart=True):
        self.language = language
        self.download_strategy = download_strategy  # см SettingsPage.py
        self.download_dir = download_dir
        self.pack_count = pack_count
        self.send_crash_notifications = send_crash_notifications
        self.rate_limit = rate_limit  # если значение 0, то лимита нет
        self.video_quality = video_quality
        self.video_extension = video_extension
        self.format = format
        self.remove_files_after_upload = remove_files_after_upload
        self.autostart = autostart
        self.retries = retries
        self.no_check_certificate = no_check_certificate
        self.audio_quality = audio_quality
        self.no_cache_dir = no_cache_dir
        self.referer = referer
        self.geo_bypass_country = geo_bypass_country
        self.keep_fragments = keep_fragments
        self.buffer_size = buffer_size
        self.write_sub = write_sub
        self.embed_subs = embed_subs
        self.save_password = save_password
        self.manual_settings = manual_settings
        self.audio_bitrate = audio_bitrate
        self.video_bitrate = video_bitrate
        self.audio_sampling_rate = audio_sampling_rate
        self.fps = fps
        self.audio_quality_str = audio_quality_str
        self.video_quality_str = video_quality_str
        self.encrypted_key = encrypted_key
        self.user_mail = user_mail
        self.ffmpeg = ffmpeg
        self.debug_browser = debug_browser
        self.enable_autostart = enable_autostart
