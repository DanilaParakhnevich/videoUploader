from PyQt5.QtCore import QSettings
from model.Settings import Settings
import os

# Этот класс предназначен для сохранения данных, необходимых для дальнейшей работы приложения
class StateService(object):

    accounts = None
    channels = None
    tabs = None
    settings = None
    events = None
    download_queue_media = None
    upload_queue_media = None

    def __init__(self):
        self.q_settings = QSettings('BuxarVideoUploaderSettings')

    def is_first_launch(self) -> bool:
        return self.q_settings.value('first_launch')

    def set_first_launch(self, first_launch: bool):
        self.q_settings.setValue('first_launch', first_launch)

    # Channels
    def save_channels(self, channels):
        StateService.channels = channels
        self.q_settings.setValue('channels', channels)

    def get_channels(self):
        if StateService.channels is None:
            StateService.channels = self.q_settings.value('channels')

            if StateService.channels is None:
                StateService.channels = list()

        return StateService.channels

    def get_channel_by_hosting(self, hosting: str):
        result = list()
        for channel in self.channels:
            if channel.hosting == hosting:
                result.append(channel)
        return result

    def get_channel_by_url(self, url):
        for channel in self.channels:
            if channel.url == url:
                return channel
        return None

    # Accounts
    def save_accounts(self, accounts):
        StateService.accounts = accounts
        self.q_settings.setValue('accounts', accounts)

    def get_accounts(self):
        if StateService.accounts is None:
            StateService.accounts = self.q_settings.value('accounts')

            if StateService.accounts is None:
                StateService.accounts = list()

        return StateService.accounts

    def get_account_by_hosting_and_login(self, hosting: str, login: str):
        for account in self.accounts:
            if account.hosting == hosting and account.login == login:
                return account
        return None

    def get_accounts_by_hosting(self, hosting: str):
        result = list()
        for account in self.accounts:
            if account.hosting == hosting:
                result.append(account)
        return result

    # Tabs
    def save_tabs_state(self, tabs):
        StateService.tabs = tabs
        self.q_settings.setValue('tabs', tabs)

    def get_last_tabs(self):
        if StateService.tabs is None:
            StateService.tabs = self.q_settings.value('tabs')

            if StateService.tabs is None:
                StateService.tabs = list()

        return StateService.tabs

    # QueueMedia
    def save_download_queue_media(self, queue_media):
        StateService.download_queue_media = queue_media
        self.q_settings.setValue('download_queue_media', queue_media)

    def get_download_queue_media(self):
        if StateService.download_queue_media is None:
            StateService.download_queue_media = self.q_settings.value('download_queue_media')

            if StateService.download_queue_media is None:
                StateService.download_queue_media = list()

        return StateService.download_queue_media

    def get_download_queue_media_by_url(self, url):
        for queue_media in self.download_queue_media:
            if queue_media.url == url:
                return queue_media
        return None

    # QueueMedia
    def save_upload_queue_media(self, queue_media):
        StateService.upload_queue_media = queue_media
        self.q_settings.setValue('upload_queue_media', queue_media)

    def get_upload_queue_media(self):
        if StateService.upload_queue_media is None:
            StateService.upload_queue_media = self.q_settings.value('upload_queue_media')

            if StateService.upload_queue_media is None:
                StateService.upload_queue_media = list()

        return StateService.upload_queue_media

    # Events
    def save_events(self, events):
        StateService.events = events
        self.q_settings.setValue('events', events)

    def get_events(self):
        if StateService.events is None:
            StateService.events = self.q_settings.value('events')

            if StateService.events is None:
                # Настройки по-умолчанию
                StateService.events = list()

        return StateService.events

    # Settings
    def save_settings(self, settings):
        StateService.settings = settings
        self.q_settings.setValue('settings', settings)

    def get_settings(self):
        if StateService.settings is None:
            StateService.settings = self.q_settings.value('settings')

            if StateService.settings is None:
                # Настройки по-умолчанию
                StateService.settings = Settings(language='Русский', download_strategy=0,
                                                 download_dir=os.pardir.__str__(), rate_limit=0, pack_count=5)
            else:
                if hasattr(StateService.settings, 'send_crash_notifications') is False:
                    StateService.settings.send_crash_notifications = True
                if hasattr(StateService.settings, 'rate_limit') is False:
                    StateService.settings.rate_limit = 0
                if hasattr(StateService.settings, 'download_strategy') is False:
                    StateService.settings.download_strategy = 0

        return StateService.settings