from model.UploadQueueMedia import UploadQueueMedia
from service.LocalizationService import get_str
from service.StateService import StateService


class EventService(object):

    def __init__(self):
        self.state_service = StateService()

    def add_event(self, event):
        events = self.state_service.get_events()
        events.append(event)

        self.state_service.save_events(events)
