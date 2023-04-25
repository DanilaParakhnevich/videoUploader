import pickle
from threading import Lock

# Этот класс предназначен для сохранения данных,
# необходимых для дальнейшей работы приложения
class StateService(object):

    accounts = None
    channels = None
    tabs = None

    channel_lock = Lock()
    last_tabs_lock = Lock()

    accounts_file = 'accounts.pkl'
    channels_file = 'channels.pkl'
    last_tabs_file = 'last_tabs.pkl'

    #Channels
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

    #Accounts
    def save_accounts(self, accounts):
        self.channel_lock.acquire()
        StateService.accounts = accounts

        with open(self.accounts_file, 'wb') as f:
            pickle.dump(accounts, f)
        self.channel_lock.release()

    def get_accounts(self):
        if not self.channel_lock.locked():
            if StateService.accounts is None:
                try:
                    with open(self.accounts_file, 'rb') as f:
                        StateService.accounts = pickle.load(f)
                except EOFError:
                    return list()
            return StateService.accounts

    def get_accounts_by_hosting(self, hosting):
        result = list()
        for account in self.accounts:
            if account.hosting == hosting:
                result.append(account)
        return result

    #Tabs
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

