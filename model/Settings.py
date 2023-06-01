class Settings(object):

    def __init__(self, language: str, download_strategy: int, rate_limit: int,
                 download_dir: str, pack_count: int = 0, send_crash_notifications: bool = True,
                 video_quality=0, format=0, remove_files_after_upload=False, autostart: bool = False,
                 retries=10, no_check_certificate=False, audio_quality=9, no_cache_dir=False, referer=''):
        self.language = language
        self.download_strategy = download_strategy  # см SettingsPage.py
        self.download_dir = download_dir
        self.pack_count = pack_count
        self.send_crash_notifications = send_crash_notifications
        self.rate_limit = rate_limit  # если значение 0, то лимита нет
        self.video_quality = video_quality
        self.format = format
        self.remove_files_after_upload = remove_files_after_upload
        self.autostart = autostart
        self.retries = retries
        self.no_check_certificate = no_check_certificate
        self.audio_quality = audio_quality
        self.no_cache_dir = no_cache_dir
        self.referer = referer
