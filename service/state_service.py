import pickle


# Этот класс предназначен для сохранения данных,
# необходимых для дальнейшей работы приложения
class StateService(object):

    channels_file = 'channels.pkl'
    last_tabs_file = 'last_tabs.pkl'

    def save_channels(self, channels):
        with open(self.channels_file, 'wb') as f:
            pickle.dump(channels, f)

    def save_tabs_state(self, tabs):
        with open(self.last_tabs_file, 'wb') as f:
            pickle.dump(tabs, f)

    def get_channels(self):
        try:
            with open(self.channels_file, 'rb') as f:
                channels = pickle.load(f)
                return channels
        except EOFError:
            return list()

    def get_last_tabs(self):
        try:
            with open(self.last_tabs_file, 'rb') as f:
                tabs = pickle.load(f)
                return tabs
        except EOFError:
            return list()

