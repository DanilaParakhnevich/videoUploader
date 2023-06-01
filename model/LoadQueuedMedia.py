from model.Account import Account


class LoadQueuedMedia(object):

    def __init__(self, url: str, hosting: str, status: int, upload_after_download: bool, format: str,
                 video_quality: str, remove_files_after_upload: bool, upload_date=None, upload_targets: list = None,
                 account: Account = None, title: str = None, description: str = None, download_dir: str = None):

        self.url = url
        # Всего 4 статуса: 0 - пауза, 1 - процесс, 2 - завершено, 3 - ошибка загрузки
        self.status = status
        self.account = account
        self.hosting = hosting
        self.upload_targets = upload_targets
        self.upload_after_download = upload_after_download
        self.upload_date = upload_date
        self.format = format
        self.video_quality = video_quality
        self.remove_files_after_upload = remove_files_after_upload
        self.title = title
        self.description = description
        self.download_dir = download_dir
