from PyQt5.QtWidgets import QTableWidgetItem

from service.LocalizationService import get_str
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
from googletrans import Translator
import time


class FacebookService(VideohostingService):

    def __init__(self):
        self.video_regex = '(https:\/\/www.facebook.com\/watch\/\?v=.*)|(https:\/\/www.facebook.com\/.*\/videos\/.*)'
        self.channel_regex = '(https:\/\/www.facebook.com\/watch\/.*\/.*)|(https:\/\/www.facebook.com\/.*)'
        self.upload_video_formats = list(['3g2', '3gp', '3gpp', 'asf', 'avi', 'dat', 'divx', 'dv', 'f4v', 'flv', 'gif',
                                          'm2ts', 'm4v', 'mkv', 'mod', 'mov', 'mp4', 'mpe', 'mpeg', 'mpeg4', 'mpg',
                                          'mts', 'nsv', 'ogm', 'ogv', 'qt', 'tod', 'ts', 'vob', 'wmv', 'webm'])
        self.duration_restriction = 240
        self.size_restriction = 4 * 1024
        self.title_size_restriction = 9_999_999_999
        self.min_title_size = 0

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            if url.__contains__('groups'):
                page.goto(f'{url}/media/videos', timeout=0)
            else:
                page.goto(f'{url}&sk=videos', timeout=0)
            page.wait_for_selector('.x6s0dn4.x9f619.x78zum5.x2lah0s.x1hshjfz.x1n2onr6.xng8ra.x1pi30zi.x1swvt13')
            time.sleep(1)
            self.scroll_page_to_the_bottom(page=page, timeout=3)
            stream_boxes = page.locator("//div[contains(@class,'xrvj5dj x5yr21d xh8yej3')]")
            for box in stream_boxes.element_handles():
                result.append(
                    VideoModel(url=str(box.query_selector('a').get_property('href')),
                               name=str(box.query_selector('img').get_property('alt')),
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
            translator = Translator()

            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url, wait_until='load', timeout=0)

            items = page.query_selector_all('.xsgj6o6.xw3qccf.x1xmf6yo.x1w6jkce.xusnbm3')
            group_elem = page.query_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.x13a6bvl.x6s0dn4.xozqiw3.x1q0g3np.xcud41i.x139jcc6.x4vbgl9.x1rdy4ex')

            user_item = None
            group_item = None

            if group_elem is not None and translator.translate(group_elem.text_content()).text == 'Invite':
                group_item = group_elem

            for item in items:
                if item.text_content() is not None and translator.translate(item.text_content()).text == 'Edit profile':
                    user_item = item

            switch_item = page.query_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xeuugli.xamitd3.x1sxyh0.xurb0ha.x10b6aqq.x1yrsyyn')

            if user_item is None and group_item is None and switch_item is not None and translator.translate(switch_item.text_content()).text == 'Switch Now' or translator.translate(switch_item.text_content()).text == 'Toggle':
                switch_item.click()

            page_item = None

            if switch_item is not None:
                page.wait_for_selector('.x78zum5.x1a02dak.x139jcc6.xcud41i.x9otpla.x1ke80iy', timeout=120_000, state='attached')
                page.wait_for_load_state('load', timeout=0)
                items = page.query_selector('.x78zum5.x1a02dak.x139jcc6.xcud41i.x9otpla.x1ke80iy').query_selector_all('.x6s0dn4.x78zum5.xl56j7k.x1608yet.xljgi0e.x1e0frkt')
                for item in items:
                    if item is not None and item.text_content() is not None and translator.translate(item.text_content()).text == 'Edit':
                        page_item = item

            if user_item is None and group_item is None and page_item is None:
                return False
            else:
                return True

    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            table_item.setText(get_str('preparing'))
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
                switch_but = page.query_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xeuugli.xamitd3.x1sxyh0.xurb0ha.x10b6aqq.x1yrsyyn')

                if switch_but is not None:
                    page.click(selector='.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xeuugli.xamitd3.x1sxyh0.xurb0ha.x10b6aqq.x1yrsyyn')

                page.wait_for_selector('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')
                page.query_selector_all('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')[1].click()
                with page.expect_file_chooser() as fc_info:
                    done_btn = page.query_selector('[aria-label="Done"]')
                    page.click(selector='.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x5yr21d')

                    if done_btn is not None:
                        page.click('[aria-label="Done"]')

            table_item.setText(get_str('uploading'))
            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            table_item.setText(get_str('ending'))

            if is_group is False:
                page.click('.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3.notranslate')
                page.wait_for_selector('.x6s0dn4.x9f619.x78zum5.x1qughib.x1pi30zi.x1swvt13.xyamay9.xh8yej3', timeout=0)
                but1 = page.query_selector('.x6s0dn4.x9f619.x78zum5.x1qughib.x1pi30zi.x1swvt13.xyamay9.xh8yej3')
            else:
                page.wait_for_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.x1qughib.x1qjc9v5.xozqiw3.x1q0g3np.x1pi30zi.x1swvt13.xyamay9.xykv574.xbmpl8g.x4cne27.xifccgj', timeout=0)
                but1 = page.query_selector_all('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.x1qughib.x1qjc9v5.xozqiw3.x1q0g3np.x1pi30zi.x1swvt13.xyamay9.xykv574.xbmpl8g.x4cne27.xifccgj')[1]

            page.keyboard.type(name)

            but1.click()

            time.sleep(30)

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True
