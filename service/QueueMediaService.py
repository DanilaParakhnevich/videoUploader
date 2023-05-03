from service.StateService import StateService


class QueueMediaService(object):

    def __init__(self):
        self.state_service = StateService()

    def add_to_the_queue(self, queue_media_list: list):
        old_queue_media = self.state_service.get_queue_media()
        old_queue_media.extend(queue_media_list)

        self.state_service.save_queue_media(old_queue_media)
        QueueMediaService.last_added_queue_media.extend(queue_media_list)

    def get_last_added_queue_media(self):
        result = QueueMediaService.last_added_queue_media.copy()
        QueueMediaService.last_added_queue_media.clear()
        return result


QueueMediaService.last_added_queue_media = list()
