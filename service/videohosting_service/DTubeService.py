from service.videohosting_service.VideohostingService import VideohostingService
from yt_dlp import YoutubeDL
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from datetime import datetime
from playwright.sync_api import sync_playwright


class DTubeService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/d.tube\/#!\/v\/.*\/.*'
        self.channel_regex = 'https:\/\/d.tube\/#!\/c\/.*'

    def get_videos_by_url(self, url, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            info = ydl.extract_info(url)
            for item in info['entries']:
                result.append(VideoModel(url=f'https://d.tube/#!/v/{item["id"]}',
                                         name=item['title'],
                                         date=datetime.fromtimestamp(item['timestamp']).__str__()))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите код')
        self.login_form.exec_()
        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://d.tube/#!/login')
            page.type('input[name=username]', login)
            page.type('input[name=privatekey]', password)
            page.keyboard.press('Enter')

            if page.url == 'https://d.tube/#!/login':
                raise Exception('Неправильные данные')

            return page.context.cookies()

    def upload_video(self, account, file_path, name, description):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://d.tube/')

            page.click(selector='.upload.icon')
            page.click(selector='[data-uploadtype="file"]')
            page.query_selector_all('.yt-simple-endpoint.style-scope.ytd-compact-link-renderer')[0].click()
            with page.expect_file_chooser() as fc_info:
                page.click(selector='[name="fileToUpload"]')
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            #сервера упали -_-