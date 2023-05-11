from gui.widgets.LoginForm import LoginForm
from model.VideoModel import VideoModel
from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
from service.Tiktok_uploader import uploadVideo


class TikTokService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https://www.tiktok.com/.*/video/.*'
        self.channel_regex = 'https://www.tiktok.com/.*'

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url)
            page.wait_for_selector('.tiktok-833rgq-DivShareLayoutMain')

            stream_boxes = page.locator("//div[contains(@class, 'tiktok-x6y88p-DivItemContainerV2')]")
            for box in stream_boxes.element_handles():
                result.append(VideoModel(url=box.query_selector('.tiktok-yz6ijl-DivWrapper').query_selector('a').get_attribute('href'),
                                         name=box.query_selector('.tiktok-1wrhn5c-AMetaCaptionLine').get_attribute('title'),
                                         date='Нет информации'))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 1, 'Введите название аккаунта')
        self.login_form.exec_()
        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://www.tiktok.com/login')
            page.wait_for_selector(selector='#main-content-homepage_hot', timeout=0)
            return page.context.cookies()

    # Пришлось использовать готовое чужое решение для выгрузки видео для TikTok, тк на сайте хорошая защита от ботов
    def upload_video(self, account, file_path, name, description, destination=None):

        for cookie in account.auth:
            if cookie['name'] == 'sessionid':
                uploadVideo(session_id=cookie['value'], video=file_path, title=name, tags=list())
                return

        raise Exception('Что-то пошло не так')
