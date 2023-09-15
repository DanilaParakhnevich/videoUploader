from model.UploadQueueMedia import UploadQueueMedia
from service.LocalizationService import get_str
from service.StateService import StateService


class QueueMediaService(object):

    def __init__(self):
        self.state_service = StateService()

    # Этот метод добавляет в список видео для очереди загрузки
    def add_to_the_download_queue(self, queue_media_list: list):
        old_queue_media = self.state_service.get_download_queue_media()
        old_queue_media.extend(queue_media_list)

        self.state_service.save_download_queue_media(old_queue_media)
        # А так же и во временный список для выборки страницей новых данных (см DownloadQueuePage.py)
        QueueMediaService.last_added_download_queue_media.extend(queue_media_list)

    def get_last_added_download_queue_media(self):
        result = QueueMediaService.last_added_download_queue_media.copy()
        QueueMediaService.last_added_download_queue_media.clear()
        return result

    # Этот метод добавляет в список видео для очереди выгрузки
    def add_to_the_upload_queue(self, queue_media):
        old_queue_media = self.state_service.get_upload_queue_media()
        old_queue_media.append(queue_media)

        self.state_service.save_upload_queue_media(old_queue_media)
        # А так же и во временный список для выборки страницей новых данных (см UploadQueuePage.py)
        QueueMediaService.last_added_upload_queue_media.append(queue_media)

    def get_last_added_upload_queue_media(self):
        result = QueueMediaService.last_added_upload_queue_media.copy()
        QueueMediaService.last_added_upload_queue_media.clear()
        return result

    def replace_to_the_upload_queue(self, queue_media):
        # А так же и в список для итемов очереди с обновленным статусом (см UploadQueuePage.py)
        QueueMediaService.last_added_temp_upload_queue_media.append(queue_media)

    def get_last_added_temp_upload_queue_media(self):
        result = QueueMediaService.last_added_temp_upload_queue_media.copy()
        QueueMediaService.last_added_temp_upload_queue_media.clear()
        return result

    def add_reauthorized_account_from_upload_page(self, old_account, account):
        QueueMediaService.reauthorized_accounts_from_upload_page.append([old_account, account])

    def get_reauthorized_accounts_from_upload_page(self):
        result = QueueMediaService.reauthorized_accounts_from_upload_page.copy()
        QueueMediaService.reauthorized_accounts_from_upload_page.clear()
        return result

    def add_reauthorized_account_from_accounts_page(self, old_account, account):
        QueueMediaService.reauthorized_accounts_from_accounts_page.append([old_account, account])

    def get_reauthorized_accounts_from_accounts_page(self):
        result = QueueMediaService.reauthorized_accounts_from_accounts_page.copy()
        QueueMediaService.reauthorized_accounts_from_accounts_page.clear()
        return result

QueueMediaService.last_added_download_queue_media = list()
QueueMediaService.last_added_upload_queue_media = list()
QueueMediaService.last_added_temp_upload_queue_media = list()
QueueMediaService.reauthorized_accounts_from_upload_page = list()
QueueMediaService.reauthorized_accounts_from_accounts_page = list()