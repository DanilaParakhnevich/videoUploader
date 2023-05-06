from model.Account import Account


class LoadQueuedMedia(object):

    def __init__(self, video_dir: str, hosting: str, status: int, account: Account,
                 destination=None, upload_date=None):

        self.video_dir = video_dir
        # Всего 4 статуса: 0 - пауза, 1 - процесс, 2 - завершено, 3 - ошибка загрузки
        self.status = status
        self.account = account
        self.hosting = hosting
        self.desctination = destination
        self.upload_date = upload_date
