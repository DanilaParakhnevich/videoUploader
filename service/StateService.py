from PyQt5.QtCore import QSettings

# Этот класс предназначен для сохранения данных,
# необходимых для дальнейшей работы приложения
class StateService(object):

    accounts = None
    channels = None
    tabs = None
    settings = None

    accounts_file = 'accounts.pkl'
    channels_file = 'channels.pkl'
    last_tabs_file = 'last_tabs.pkl'

    def __init__(self):
        self.settings = QSettings('BuharVideoUploaderSettings')

    # Channels
    def save_channels(self, channels):
        StateService.channels = channels
        self.settings.setValue('channels', channels)

    def get_channels(self):
        if StateService.channels is None:
            StateService.channels = self.settings.value('channels')

            if StateService.channels is None:
                StateService.channels = list()

        return StateService.channels

    def get_channel_by_url(self, url):
        for channel in self.channels:
            if channel.url == url:
                return channel
        return None

    # Accounts
    def save_accounts(self, accounts):
        StateService.accounts = accounts
        self.settings.setValue('accounts', accounts)

    def get_accounts(self):
        if StateService.accounts is None:
            StateService.accounts = self.settings.value('accounts')

            if StateService.accounts is None:
                StateService.accounts = list()

        return StateService.accounts

    def get_accounts_by_hosting(self, hosting):
        result = list()
        for account in self.accounts:
            if account.hosting == hosting:
                result.append(account)
        return result

    # Tabs
    def save_tabs_state(self, tabs):
        StateService.tabs = tabs
        self.settings.setValue('tabs', tabs)

    def get_last_tabs(self):
        if StateService.tabs is None:
            StateService.tabs = self.settings.value('tabs')

            if StateService.tabs is None:
                StateService.tabs = list()

        return StateService.tabs

