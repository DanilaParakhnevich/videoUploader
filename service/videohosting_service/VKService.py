import sys

from PyQt5.QtWidgets import QTableWidgetItem
from playwright.sync_api import sync_playwright

from service.LocalizationService import get_str
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
        self.title_size_restriction = 3_772
        self.min_title_size = 1
        self.description_size_restriction = 9_999_999_999
        self.duration_restriction = sys.maxsize
        self.size_restriction = 2 * 1024
        self.upload_video_formats = list(['avi', 'mp4', '3gp', 'mpeg', 'mov', 'flv', 'f4v', 'wmv', 'mkv', 'webm', 'vob',
                                          'rmvb', 'm4v', 'mpg', 'ogv', 'ts', 'm2ts', 'mts', 'mxf', 'torrent'])

    def get_videos_by_url(self, url, account=None):
        videos = list()

        if account is None:
            result = list()

            with sync_playwright() as p:
                context = self.new_context(p=p, headless=True, use_user_agent_arg=True)

                page = context.new_page()
                page.goto(url, timeout=0, wait_until='domcontentloaded')
                page.wait_for_selector('.page_block.redesigned-cover-block')
                button = page.query_selector('li[data-tab="videos"]')

                if button is None:
                    raise Exception()

                button.click()
                page.click('a[href*="/video/"]', timeout=0)

                self.scroll_page_to_the_bottom(page=page)
                stream_boxes = page.locator("//div[contains(@class,'_video_item ge_video_item_')]")
                for box in stream_boxes.element_handles():
                    result.append(
                        VideoModel(url=str(box.query_selector("a").get_property("href")),
                                   name=str(box.query_selector(".VideoCard__title").text_content()),
                                   date=str(box.query_selector('.VideoCard__extendedInfoUpdated').text_content())))

            return result
        else:
            vk_session = vk_api.VkApi(token=account.auth['access_token'])
            i = 0
            prev_size = 1
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
                                           date=str(
                                               datetime.fromtimestamp(video['date']).strftime('%Y-%m-%d %H:%M:%S'))))
                        except:
                            print(video)

        return videos

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(form, hosting, self, 2, get_str('enter_login'), get_str('enter_pas'), title=title, username_val=login, password_val=password, relogin=can_relogin)
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

    def validate_url_by_account(self, url: str, account) -> int:
        vk_session = vk_api.VkApi(token=account.auth['access_token'])

        user_id = account.auth['user_id']

        with vk_api.VkRequestsPool(vk_session) as pool:
            response = pool.method('utils.resolveScreenName', {
                'screen_name': url.split('/')[3]
            })

        if response.result['type'] == 'group':
            with vk_api.VkRequestsPool(vk_session) as pool:
                response = pool.method('groups.getById', {
                    'group_id': response.result['object_id']
                })
            return response.result[0]['is_admin'] == 1
        else:
            return response.result["object_id"] == user_id

    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        if table_item is not None:
            table_item.setText(get_str('preparing'))
        vk_session = vk_api.VkApi(token=account.auth['access_token'])

        with vk_api.VkRequestsPool(vk_session) as pool:
            response = pool.method('utils.resolveScreenName', {
                'screen_name': destination.split('/')[3]
            })

        if response.result['type'] == 'group':
            object_id = response.result["object_id"]
        else:
            object_id = None

        if table_item is not None:
            table_item.setText(get_str('uploading'))

        vk_upload = vk_api.VkUpload(vk_session)
        vk_upload.video(video_file=file_path, name=name, group_id=object_id,
                        description=description if description is not None else '')

    def handle_auth(self):
        form = AuthenticationConfirmationForm(self.login_form)
        form.exec_()

        return form.code_edit.text()

    def check_auth(self, account) -> bool:
        return True

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True
