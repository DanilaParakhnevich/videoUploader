from service.videohosting_service.VideohostingService import VideohostingService
from service.StateService import StateService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
import vk_api
import requests
from datetime import datetime

class VKService(VideohostingService):

    form = None
    state_service = StateService()

    def get_videos_by_link(self, link, account=None):
        vk_session = vk_api.VkApi(token=account.auth['access_token'])

        i = 0
        prev_size = 1
        videos = list()
        with vk_api.VkRequestsPool(vk_session) as pool:
            while prev_size != 0:
                response = pool.method('video.get', {
                    'count': 200,
                    'offset': 200 * i
                })
                i += 1

                pool.execute()

                prev_size = len(response.result['items'])
                for video in response.result['items']:
                    try:
                        videos.append(
                            VideoModel(url=video['player'],
                                       name=video['title'],
                                       date=str(datetime.fromtimestamp(video['date']).strftime('%Y-%m-%d %H:%M:%S'))))
                    except:
                        print(video)

        return videos

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        session = requests.Session()

        response = self.auth(login, password, session)

        if 'validation_sid' in response:
            session.get("https://api.vk.com/method/auth.validatePhone",
                        params={'sid': response['validation_sid'], 'v': '5.131'})
            self.auth(login, password, session)
            response = self.auth(login, password, session, two_fa=True, code=self.handle_auth())
        elif 'error' in response:
            raise Exception(response['error_description'])

        return response

    def auth(self, login: str, password: str, session: requests.Session, two_fa: bool = False, code: str = None):
        return session.get(f'https://oauth.vk.com/token', params={
            'grant_type': 'password',
            'client_id': '6146827',
            'client_secret': 'qVxWRF1CwHERuIrKBnqe',
            'username': login,
            'password': password,
            'v': '5.130',
            '2fa_supported': '1',
            'force_sms': '1' if two_fa else '0',
            'code': code if two_fa else None
        }).json()

    def handle_auth(self):
        form = AuthenticationConfirmationForm(self.login_form)
        form.exec_()
        return form.code_edit.text()
