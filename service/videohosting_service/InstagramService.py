from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from datetime import datetime
from instascrape import Instascraper
from playwright.sync_api import sync_playwright
import time
import re


class InstagramService(VideohostingService):

    url = 'https://www.instagram.com/'

    def get_videos_by_link(self, link, account=None):
        try:
            with Instascraper() as insta:
                posts = insta.profile(link.replace(self.url, '').replace('/', '')).timeline_posts()
                result = list()
                for post in posts:
                    result.append(VideoModel(post.url, post.caption, str(datetime.fromtimestamp(post.created_time).strftime('%Y-%m-%d %H:%M:%S'))))
        except:
            if account is not None:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=False)
                    context = browser.new_context()
                    context.add_cookies(account.auth)
                    page = context.new_page()
                    page.goto(link)

                    page.evaluate(
                        """
                        var intervalID = setInterval(function () {
                            var scrollingElement = (document.scrollingElement || document.body);
                            scrollingElement.scrollTop = scrollingElement.scrollHeight;
                        }, 200);

                        """
                    )
                    prev_height = None
                    while True:
                        curr_height = page.evaluate('(window.innerHeight + window.scrollY)')
                        if not prev_height:
                            prev_height = curr_height
                            time.sleep(1)
                        elif prev_height == curr_height:
                            page.evaluate('clearInterval(intervalID)')
                            break
                        else:
                            prev_height = curr_height
                            time.sleep(1)

                    result = list()
                    stream_boxes = page.locator("//div[contains(@class,'_aagv')]")
                    for box in stream_boxes.element_handles():
                        result.append(
                            VideoModel(url=box.owner_frame().__getattribute__('url'),
                                       name='Нет информации',
                                       date=re.search(' on (.*). May',
                                                      str(box.query_selector('img').get_property('alt'))).group(1)))
                return result
            else:
                raise Exception('Приватный профиль. Необходима авторизация')
        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите пароль')
        self.login_form.exec_()
        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://www.instagram.com/')
            page.type('input[name="username"]', login)
            page.type('input[name="password"]', password)
            page.click('._acap')
            page.wait_for_selector('._aauo', timeout=0)
            return page.context.cookies()
