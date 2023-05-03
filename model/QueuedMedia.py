from model.Account import Account


class QueuedMedia(object):

    def __init__(self, url: str, hosting: str, status: int, upload_after_download: bool, account: Account = None):
        self.url = url
        # Всего 4 статуса: 0 - пауза, 1 - процесс, 2 - завершено, 3 - ошибка загрузки
        self.status = status
        self.account = account
        self.hosting = hosting
        self.upload_after_download = upload_after_download
