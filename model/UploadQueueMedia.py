from model.Account import Account


class UploadQueueMedia(object):

    def __init__(self, video_dir: str, hosting: str, status: int, account: Account, remove_files_after_upload,
                 destination=None, upload_date=None, title=None, description=None, error_name=None):

        self.video_dir = video_dir
        # Всего 4 статуса: 0 - пауза, 1 - процесс, 2 - завершено, 3 - ошибка загрузки
        self.status = status
        self.account = account
        self.hosting = hosting
        self.destination = destination
        self.upload_date = upload_date
        self.title = title
        self.description = description
        self.remove_files_after_upload = remove_files_after_upload
        self.error_name = error_name
