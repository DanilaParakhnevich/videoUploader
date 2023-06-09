from service.LocalizationService import get_str
from service.LoggingService import log_error
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import time


class FacebookService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.facebook.com\/watch\/\?v=.*'
        self.channel_regex = '(https:\/\/www.facebook.com\/watch\/.*\/.*)|(https:\/\/www.facebook.com\/.*)'
        self.upload_video_formats = list(['3g2', '3gp', '3gpp', 'asf', 'avi', 'dat', 'divx', 'dv', 'f4v', 'flv', 'gif',
                                          'm2ts', 'm4v', 'mkv', 'mod', 'mov', 'mp4', 'mpe', 'mpeg', 'mpeg4', 'mpg',
                                          'mts', 'nsv', 'ogm', 'ogv', 'qt', 'tod', 'ts', 'vob', 'wmv', 'webm'])
        self.duration_restriction = 240
        self.size_restriction = 4 * 1024
        self.title_size_restriction = 9_999_999_999

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            page.goto(url, timeout=0)
            page.wait_for_selector('.x6s0dn4.x9f619.x78zum5.x2lah0s.x1hshjfz.x1n2onr6.xng8ra.x1pi30zi.x1swvt13')
            buttons = page.query_selector_all('.x6s0dn4.x9f619.x78zum5.x2lah0s.x1hshjfz.x1n2onr6.xng8ra.x1pi30zi.x1swvt13')
            if len(buttons) == 5:
                for button in buttons:
                    if button.text_content() == 'Media':
                        button.click(timeout=0)
                time.sleep(1)
                page.query_selector('[href*="/media/videos"]').click(timeout=0, no_wait_after=True)
                self.scroll_page_to_the_bottom(page=page, timeout=3)
                stream_boxes = page.locator("//div[contains(@class,'xrvj5dj x5yr21d xh8yej3')]")
                for box in stream_boxes.element_handles():
                    result.append(
                        VideoModel(url=str(box.query_selector('a').get_property('href')),
                                   name=str(box.query_selector('img').get_property('alt')),
                                   date=get_str('no_info')))

            else:
                buttons[5].click(timeout=0)
                time.sleep(1)
                self.scroll_page_to_the_bottom(page=page, timeout=3)
                stream_boxes = page.locator("//div[contains(@class,'x9f619 x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1n2onr6')]")
                for box in stream_boxes.element_handles():
                    if box.query_selector('a') is not None:
                        result.append(
                            VideoModel(url=str(box.query_selector('a').get_property('href')),
                                       name=get_str('no_info'),
                                       date=get_str('no_info')))

        return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False, use_user_agent_arg=True)
            page = context.new_page()
            page.goto('https://mbasic.facebook.com')
            page.type('input[name=email]', login)
            page.type('input[name=pass]', password)
            page.keyboard.press('Enter')

            page.wait_for_selector('#mbasic_inline_feed_composer', timeout=0)
            return page.context.cookies()

    def validate_url_by_account(self, url: str, account) -> int:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url, timeout=0)

            user_item = page.query_selector('div[aria-label="Edit profile"]')
            group_item = page.query_selector('div[aria-label="Invite"]')
            if user_item is None and group_item is None and page.query_selector('div[aria-label="Switch Now"]') is not None:
                page.query_selector('div[aria-label="Switch Now"]').click()
                try:
                    page.wait_for_selector('div[aria-label="Edit"]', timeout=60_000)
                except:
                    log_error('Switch now есть, а Edit нет(')

            page_item = page.query_selector('div[aria-label="Edit"]')

            if user_item is None and group_item is None and page_item is None:
                return False
            else:
                return True

    def upload_video(self, account, file_path, name, description, destination: str = None):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(destination, wait_until='domcontentloaded')

            is_group = False

            if destination.__contains__('groups'):
                with page.expect_file_chooser() as fc_info:
                    page.wait_for_selector('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')
                    page.query_selector_all('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')[1].click()
                    is_group = True
            else:
                switch_but = page.query_selector('[aria-label="Switch Now"]')

                if switch_but is not None:
                    page.click(selector='[aria-label="Switch Now"]')

                page.wait_for_selector('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')
                page.query_selector_all('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')[1].click()
                with page.expect_file_chooser() as fc_info:
                    done_btn = page.query_selector('[aria-label="Done"]')
                    page.click(selector='.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x5yr21d')

                    if done_btn is not None:
                        page.click('[aria-label="Done"]')

            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            page.wait_for_selector('[role="button"][aria-label="Post"]', timeout=0)
            if is_group is False:
                page.click('[aria-label="What\'s on your mind?"]')

            page.keyboard.type(name)

            but1 = page.query_selector('[role="button"][aria-label="Post"]')

            but1.click()

            time.sleep(30)

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True
