from service.videohosting_service.VideohostingService import VideohostingService
from pyrogram import Client
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm


class TelegramService(VideohostingService):

    api_id = 21915718
    api_hash = "e4fda4b7d7ab5c8f27df56c71fbe44d9"

    def __init__(self):
        self.video_regex = 'https:\/\/t.me/.*\/.*'
        self.channel_regex = 'https:\/\/t.me\/.*'
        self.upload_video_formats = list(['3g2', '3gp', '3gpp', 'asf', 'avi', 'dat', 'divx', 'dv', 'f4v', 'flv', 'gif',
                                          'm2ts', 'm4v', 'mkv', 'mod', 'mov', 'mp4', 'mpe', 'mpeg', 'mpeg4', 'mpg',
                                          'mts', 'nsv', 'ogm', 'ogv', 'qt', 'tod', 'ts', 'vob', 'wmv'])
        self.duration_restriction = 240
        self.size_restriction = 2 * 1024

    def get_videos_by_url(self, url, account=None):
        app = Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash, workdir='service/videohosting_service/tmp')

        result = list()

        with app:
            for message in app.get_chat_history(chat_id='durov'):
                if message.video is not None:
                    result.append(VideoModel(url=message.link, name=message.caption, date=str(message.date)))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите номер телефона')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, phone_number, password=None):
        app = Client(name=phone_number, api_id=self.api_id, api_hash=self.api_hash, workdir='service/videohosting_service/tmp')

        app.connect()
        if app.is_connected is False:
            sent_code_info = app.send_code(phone_number)
            phone_code = self.handle_auth()

            app.sign_in(phone_number, sent_code_info.phone_code_hash, phone_code)

        return True

    def upload_video(self, account, file_path, name, description):

        app = Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                     workdir='service/videohosting_service/tmp')
        app.send_video()
        # send_video нужно просить написать канал для отправки
        # app.connect()
        # sent_code_info = app.send_code(phone_number)
        # phone_code = self.handle_auth()
        # app.sign_in(phone_number, sent_code_info.phone_code_hash, phone_code)

        return True

    def handle_auth(self):
        form = AuthenticationConfirmationForm(self.login_form)
        form.exec_()

        return form.code_edit.text()

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True

    def validate_special_source(self, account, source_name) -> bool:
        app = Client(name=account.login, api_id=self.api_id, api_hash=self.api_hash,
                     workdir='service/videohosting_service/tmp')
        app.get_chat_history(chat_id=source_name)