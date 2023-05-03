from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from datetime import datetime
from instascrape import Instascraper
from playwright.sync_api import sync_playwright
import re


class InstagramService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.instagram.com\/p\/.*\/'
        self.channel_regex = 'https:\/\/www.instagram.com\/.*/'

    def get_videos_by_url(self, url, account=None):
        result = list()

        try:
            with Instascraper() as insta:
                posts = insta.profile(url.replace('https://www.instagram.com/', '').replace('/', '')).timeline_posts()
                for post in posts:
                    result.append(VideoModel(post.url, post.caption, str(datetime.fromtimestamp(post.created_time).strftime('%Y-%m-%d %H:%M:%S'))))

        except:
            if account is not None:
                with sync_playwright() as p:
                    context = self.new_context(p=p, headless=True)
                    context.add_cookies(account.auth)
                    page = context.new_page()
                    page.goto(url)
                    self.scroll_page_to_the_bottom(page=page)
                    stream_boxes = page.locator("//div[contains(@class,'_aagv')]")

                    for box in stream_boxes.element_handles():
                        not_parsed_date = box.query_selector('img').get_property('alt')
                        if re.search(' on (.*).', str(not_parsed_date)) is not None:
                            date = re.search(' on (.*).', str(box.query_selector('img').get_property('alt'))).group(1)
                        else:
                            date = 'Нет информации'

                        result.append(
                            VideoModel(url=box.owner_frame().__getattribute__('url'),
                                       name='Нет информации',
                                       date=date))

            else:
                raise Exception('Приватный профиль. Необходима авторизация')
        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите пароль')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False)
            page = context.new_page()
            page.goto('https://www.instagram.com/')
            page.type('input[name="username"]', login)
            page.type('input[name="password"]', password)
            page.click('._acap')
            page.wait_for_selector('._aauo', timeout=0)

            return page.context.cookies()
