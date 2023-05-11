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


QueueMediaService.last_added_download_queue_media = list()
QueueMediaService.last_added_upload_queue_media = list()
