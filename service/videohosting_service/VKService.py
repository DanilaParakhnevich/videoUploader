from service.videohosting_service.VideohostingService import VideohostingService
from service.StateService import StateService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
import vk_api
from _datetime import datetime
import requests


def auth(login: str, password: str, session: requests.Session, two_fa: bool = False, code: str = None):
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


class VKService(VideohostingService):

    state_service = StateService()

    def __init__(self):
        self.video_regex = 'https:\/\/vk.com\/.*\/=video-.*'
        self.channel_regex = 'https:\/\/vk.com\/.*'

    def get_videos_by_url(self, url, account=None):
        vk_session = vk_api.VkApi(token=account.auth['access_token'])
        i = 0
        prev_size = 1
        videos = list()
        with vk_api.VkRequestsPool(vk_session) as pool:
            response = pool.method('utils.resolveScreenName', {
                'screen_name': url.split('/')[3]
            })

        if response.result['type'] == 'group':
            object_id = f'-{response.result["object_id"]}'
        else:
            object_id = response.result['object_id']

        with vk_api.VkRequestsPool(vk_session) as pool:

            while prev_size != 0:
                response = pool.method('video.get', {
                    'owner_id': object_id,
                    'count': 200,
                    'offset': 200 * i
                })
                i += 1

                pool.execute()

                prev_size = len(response.result['items'])
                for video in response.result['items']:
                    try:
                        videos.append(
                            VideoModel(url=f'https://vk.com/video?z=video{video["owner_id"]}_{video["id"]}',
                                       name=video['title'],
                                       date=str(datetime.fromtimestamp(video['date']).strftime('%Y-%m-%d %H:%M:%S'))))
                    except:
                        print(video)

        return videos

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите пароль')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        session = requests.Session()
        response = auth(login, password, session)

        if 'validation_sid' in response:
            session.get("https://api.vk.com/method/auth.validatePhone",
                        params={'sid': response['validation_sid'], 'v': '5.131'})
            auth(login, password, session)
            response = auth(login, password, session, two_fa=True, code=self.handle_auth())
        elif 'error' in response:
            raise Exception(response['error_description'])

        return response

    def upload_video(self, account, file_path, name, description):
        vk_session = vk_api.VkApi(token=account.auth['access_token'])

        vk_upload = vk_api.VkUpload(vk_session)
        vk_upload.video(video_file=file_path, name=name, description=description)

    def handle_auth(self):
        form = AuthenticationConfirmationForm(self.login_form)
        form.exec_()

        return form.code_edit.text()
