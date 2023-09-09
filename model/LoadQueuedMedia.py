import uuid

from model.Account import Account


class LoadQueuedMedia(object):
    video_dir = None

    def __init__(self, media_id: uuid, url: str, hosting: str, status: int, upload_after_download: bool, format: str,
                 video_quality: str, video_extension:str, remove_files_after_upload: bool, upload_date=None, upload_in=None, upload_targets: list = None,
                 account: Account = None, title: str = None, description: str = None, download_dir: str = None, video_size: str = None,
                 manual_settings=True, audio_quality_str=0, video_quality_str=0, audio_bitrate=0, video_bitrate=0,
                 audio_sampling_rate=0, fps=0, status_name = None, wait_for=None, load_in=None, load_date=None, download_strategy=0, pack_count=0):

        self.id = media_id
        self.url = url
        self.wait_for = wait_for
        self.load_in = load_in
        self.load_date = load_date
        # Всего 4 статуса: 0 - пауза, 1 - процесс, 2 - завершено, 3 - ошибка загрузки
        self.status = status
        self.account = account
        self.hosting = hosting
        self.upload_targets = upload_targets
        self.upload_after_download = upload_after_download
        self.upload_date = upload_date
        self.format = format
        self.video_quality = video_quality
        self.video_extension = video_extension
        self.remove_files_after_upload = remove_files_after_upload
        self.title = title
        self.description = description
        self.download_dir = download_dir
        self.video_size = video_size
        self.downloaded_dir = None
        self.manual_settings = manual_settings
        self.audio_bitrate = audio_bitrate
        self.video_bitrate = video_bitrate
        self.audio_sampling_rate = audio_sampling_rate
        self.fps = fps
        self.audio_quality_str = audio_quality_str
        self.video_quality_str = video_quality_str
        self.status_name = status_name
        self.upload_in = upload_in
        self.download_strategy = download_strategy
        self.pack_count = pack_count
