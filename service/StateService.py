import uuid

from PyQt5.QtCore import QSettings, QSize, QDir

from model.Event import Event
from model.LicenseModel import LicenseModel
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

            for account in StateService.accounts:
                if account.hosting == 'Rutube' and type(account.auth) != str:
                    account.auth = uuid.uuid4()

        return StateService.accounts

    def get_account_by_hosting_and_login(self, hosting: str, login: str, upload_target=None):
        for account in self.accounts:
            if account.hosting == hosting and account.login == login:
                if upload_target is not None and account.url == upload_target:
                    return account
                elif upload_target is None:
                    return account
        return None

    def get_account_by_hosting_and_url(self, hosting: str, url: str):
        for account in self.accounts:
            if account.hosting == hosting and account.url == url:
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

            for tab in StateService.tabs:
                if hasattr(tab, 'video_extension') is False:
                    tab.video_extension = 5
                if hasattr(tab, 'download_dir') is False:
                    tab.download_dir = StateService.settings.download_dir
                if hasattr(tab, 'video_list') is False:
                    tab.video_list = list()
                if hasattr(tab, 'manual_settings') is False:
                    tab.manual_settings = True
                if hasattr(tab, 'video_quality_str') is False:
                    tab.video_quality_str = self.get_settings().video_quality_str
                if hasattr(tab, 'video_bitrate') is False:
                    tab.video_bitrate = self.get_settings().video_bitrate
                if hasattr(tab, 'audio_quality_str') is False:
                    tab.audio_quality_str = self.get_settings().audio_quality_str
                if hasattr(tab, 'audio_bitrate') is False:
                    tab.audio_bitrate = self.get_settings().audio_bitrate
                if hasattr(tab, 'audio_sampling_rate') is False:
                    tab.audio_sampling_rate = self.get_settings().audio_sampling_rate
                if hasattr(tab, 'fps') is False:
                    tab.fps = self.get_settings().fps
                if hasattr(tab, 'current_channel') is False:
                    tab.current_channel = tab.channel

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

            for queue_media in StateService.download_queue_media:
                if hasattr(queue_media, 'id') is False:
                    queue_media.id = str(uuid.uuid4())
                if queue_media.status == 3 and hasattr(queue_media, 'status_name') is False:
                    queue_media.status_name = 'technical_error'
                if hasattr(queue_media, 'upload_in') is False:
                    queue_media.upload_in = None
                if hasattr(queue_media, 'load_in') is False:
                    queue_media.load_in = 0
                if hasattr(queue_media, 'wait_for') is False:
                    queue_media.wait_for = None
                if hasattr(queue_media, 'load_date') is False:
                    queue_media.load_date = None
                if hasattr(queue_media, 'download_strategy') is False:
                    queue_media.download_strategy = self.get_settings().download_strategy
                if hasattr(queue_media, 'pack_count') is False:
                    queue_media.pack_count = self.get_settings().pack_count

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

            for queue_media in StateService.upload_queue_media:
                if hasattr(queue_media, 'error_name') is False:
                    queue_media.error_name = None
                if hasattr(queue_media, 'id') is False:
                    queue_media.id = str(uuid.uuid4())
                if hasattr(queue_media, 'upload_in') is False:
                    queue_media.upload_in = None
                if hasattr(queue_media, 'wait_for') is False:
                    queue_media.wait_for = None
                if hasattr(queue_media, 'hash') is False:
                    queue_media.hash = None

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
            else:
                if len(StateService.events) != 0:
                    for index in range(len(StateService.events) - 1):
                        if type(StateService.events[index]) == str:
                            StateService.events[index] = Event(StateService.events[index])

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
                if hasattr(StateService.settings, 'video_quality') is False:
                    StateService.settings.video_quality = 0
                if hasattr(StateService.settings, 'remove_files_after_upload') is False:
                    StateService.settings.remove_files_after_upload = False
                if hasattr(StateService.settings, 'format') is False:
                    StateService.settings.format = 0
                if hasattr(StateService.settings, 'autostart') is False:
                    StateService.settings.autostart = False
                if hasattr(StateService.settings, 'retries') is False:
                    StateService.settings.retries = 10
                if hasattr(StateService.settings, 'no_check_certificate') is False:
                    StateService.settings.no_check_certificate = False
                if hasattr(StateService.settings, 'audio_quality') is False:
                    StateService.settings.audio_quality = 9
                if hasattr(StateService.settings, 'no_cache_dir') is False:
                    StateService.settings.no_cache_dir = False
                if hasattr(StateService.settings, 'referer') is False:
                    StateService.settings.referer = ''
                if hasattr(StateService.settings, 'geo_bypass_country') is False:
                    StateService.settings.geo_bypass_country = ''
                if hasattr(StateService.settings, 'keep_fragments') is False:
                    StateService.settings.keep_fragments = False
                if hasattr(StateService.settings, 'buffer_size') is False:
                    StateService.settings.buffer_size = 1024
                if hasattr(StateService.settings, 'write_sub') is False:
                    StateService.settings.write_sub = False
                if hasattr(StateService.settings, 'embed_subs') is False:
                    StateService.settings.embed_subs = False
                if hasattr(StateService.settings, 'video_extension') is False:
                    StateService.settings.video_extension = 5
                elif type(StateService.settings.video_extension) is list:
                    StateService.settings.video_extension = 5
                if hasattr(StateService.settings, 'save_password') is False:
                    StateService.settings.save_password = True
                if hasattr(StateService.settings, 'manual_settings') is False:
                    StateService.settings.manual_settings = False
                if hasattr(StateService.settings, 'audio_quality_str') is False:
                    StateService.settings.audio_quality_str = 0
                if hasattr(StateService.settings, 'video_quality_str') is False:
                    StateService.settings.video_quality_str = 0
                if hasattr(StateService.settings, 'audio_bitrate') is False:
                    StateService.settings.audio_bitrate = 0
                if hasattr(StateService.settings, 'video_bitrate') is False:
                    StateService.settings.video_bitrate = 0
                if hasattr(StateService.settings, 'audio_sampling_rate') is False:
                    StateService.settings.audio_sampling_rate = 0
                if hasattr(StateService.settings, 'fps') is False:
                    StateService.settings.fps = 0
                if hasattr(StateService.settings, 'debug_browser') is False:
                    StateService.settings.debug_browser = False
                if hasattr(StateService.settings, 'user_mail') is False:
                    StateService.settings.user_mail = None
                if hasattr(StateService.settings, 'encrypted_key') is False:
                    StateService.settings.encrypted_key = None
                if hasattr(StateService.settings, 'enable_autostart') is False:
                    StateService.settings.enable_autostart = True
        return StateService.settings

    def get_license_model(self):
        value = self.q_settings.value('license_model')

        if value is None:
            value = LicenseModel()

        if value.user_mail is None and self.get_settings().user_mail is not None:
            value.encrypted_key = list(self.get_settings().encrypted_key)
            value.user_mail = list(self.get_settings().user_mail)
            self.save_license_model(value)

        return value

    def save_license_model(self, license_model):
        self.q_settings.setValue('license_model', license_model)

    # GUI

    def get_type_url_form_size(self):
        size = self.q_settings.value('type_url_form_size')

        if size is None:
            return QSize(500, 120)
        return size

    def save_type_url_form_size(self, size: QSize):
        self.q_settings.setValue('type_url_form_size', size)

    def save_events_column_width(self, width):
        self.q_settings.setValue('events_column_width', width)

    def get_events_column_width(self):
        result = self.q_settings.value('events_column_width')

        if result is None:
            return 145
        return int(result)

    def save_events_list_height(self, height):
        self.q_settings.setValue('events_list_height', height)

    def get_events_list_height(self):
        result = self.q_settings.value('events_list_height')

        if result is None:
            return 120
        return int(result)

    def add_loaded_video_to_the_history(self, link, video_quality, video_extension):
        history = self.q_settings.value('history')

        if history is None:
            history = list()

        history.append({
            'link': link,
            'quality': video_quality,
            'ext': video_extension
        })
        self.q_settings.setValue('history', history)

    def if_video_has_been_loaded(self, link, video_quality, video_extension):
        history = self.q_settings.value('history')

        if history is not None:
            for video in history:
                if video['link'] == link and video['quality'] == video_quality and video['ext'] == video_extension:
                    return True
        else:
            self.q_settings.setValue('history', list())

        return False

    def save_tab_column_weight(self, name: str, index, width):
        self.q_settings.setValue(f'width_{name}_{index}', width)

    def get_tab_column_weight(self, name: str, index, start_width=590, count=5):
        result = self.q_settings.value(f'width_{name}_{index}')

        if result is None or int(result) == 0:
            return start_width / count
        return int(result)

    def save_column_row(self, name, index, width):
        self.q_settings.setValue(f'{name}_{index}', width)

    def column_row(self, name, index):
        value = self.q_settings.value(f'{name}_{index}')
        if value is not None:
            return int(value)
        return value

    def save_name(self, name, value):
        self.q_settings.setValue(name, value)

    def get_name(self, name):
        value = self.q_settings.value(name)
        if value is None:
            return ''
        return value

    def save_main_window_size(self, width, height):
        self.q_settings.setValue('main_window_size', [width, height])

    def get_main_window_size(self):
        result = self.q_settings.value('main_window_size')

        if result is None:
            return [950, 600]

        return [int(result[0]), int(result[1])]

    def get_accounts_list_widget_size(self):
        result = self.q_settings.value('accounts_list_widget')

        if result is None:
            return [500, 120]

        return [int(result[0]), int(result[1])]

    def save_accounts_list_widget_size(self, width, height):
        self.q_settings.setValue('accounts_list_widget', [width, height])

    def save_dir(self, directory):
        self.q_settings.setValue('dir', directory)

    def get_dir(self):
        return str(self.q_settings.value('dir', QDir.homePath()))

    def set_error_status(self, value):
        self.q_settings.setValue('error', value)

    def is_error_appeared(self):
        if self.q_settings.value('error') is None:
            return False

        return False if self.q_settings.value('error') == 'false' else True

