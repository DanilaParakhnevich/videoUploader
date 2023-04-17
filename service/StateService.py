import pickle
from threading import Lock

import model.channel


# Этот класс предназначен для сохранения данных,
# необходимых для дальнейшей работы приложения
class StateService(object):

    channels = None
    tabs = None

    channel_lock = Lock()
    last_tabs_lock = Lock()

    channels_file = 'channels.pkl'
    last_tabs_file = 'last_tabs.pkl'

    def save_channels(self, channels):
        self.channel_lock.acquire()
        StateService.channels = channels

        with open(self.channels_file, 'wb') as f:
            pickle.dump(channels, f)
        self.channel_lock.release()

    def get_channels(self):
        if not self.channel_lock.locked():
            if StateService.channels is None:
                try:
                    with open(self.channels_file, 'rb') as f:
                        StateService.channels = pickle.load(f)
                except EOFError:
                    return list()
            return StateService.channels

    def get_channel_by_url(self, url):
        for channel in self.channels:
            if channel.url == url:
                return channel
        return None

    def save_tabs_state(self, tabs):
        self.last_tabs_lock.acquire()
        StateService.tabs = tabs

        with open(self.last_tabs_file, 'wb') as f:
            pickle.dump(tabs, f)
        self.last_tabs_lock.release()

    def get_last_tabs(self):
        if not self.last_tabs_lock.locked():
            if StateService.tabs is None:
                try:
                    with open(self.last_tabs_file, 'rb') as f:
                        StateService.tabs = pickle.load(f)
                except EOFError:
                    return list()
            return StateService.tabs

