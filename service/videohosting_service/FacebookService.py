from PyQt5.QtWidgets import QTableWidgetItem

from service.LocalizationService import get_str
from service.StateService import StateService
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
from googletrans import Translator
import time


class FacebookService(VideohostingService):

    def __init__(self):
        self.video_regex = '(https:\/\/www.facebook.com\/watch\/\?v=.*)|(https:\/\/www.facebook.com\/.*\/videos\/.*)'
        self.channel_regex = '(https:\/\/www.facebook.com\/watch\/.*\/.*)|(https:\/\/www.facebook.com\/.*)|(https:\/\/web.facebook.com\/.*)'
        self.upload_video_formats = list(['3g2', '3gp', '3gpp', 'asf', 'avi', 'dat', 'divx', 'dv', 'f4v', 'flv', 'gif',
                                          'm2ts', 'm4v', 'mkv', 'mod', 'mov', 'mp4', 'mpe', 'mpeg', 'mpeg4', 'mpg',
                                          'mts', 'nsv', 'ogm', 'ogv', 'qt', 'tod', 'ts', 'vob', 'wmv', 'webm'])
        self.duration_restriction = 240
        self.size_restriction = 4 * 1024
        self.title_size_restriction = 9_999_999_999
        self.min_title_size = 0

    def get_videos_by_url(self, url: str, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True)

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            if url.endswith('/'):
                url = url[0:len(url) - 1]

            video_selector = '.xrvj5dj.x5yr21d.xh8yej3'
            if url.__contains__('groups'):
                page.goto(f'{url}/media/videos', timeout=0)

            else:
                page.goto(f'{url}&sk=videos', timeout=0)
                try:
                    page.wait_for_selector('.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv.x1lliihq.x5yr21d.x1n2onr6.xh8yej3')
                    video_selector = '.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv.x1lliihq.x5yr21d.x1n2onr6.xh8yej3'
                except:
                    video_selector = '.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv[aria-hidden="true"]'

            page.wait_for_selector(video_selector)

            time.sleep(1)
            self.scroll_page_to_the_bottom(page=page, timeout=3)
            stream_boxes = page.query_selector_all(video_selector)
            for box in stream_boxes.copy():
                if box.get_attribute('href') is not None or (box.query_selector('a') is not None and box.query_selector('a').get_attribute('href') is not None):
                    if video_selector == '.xrvj5dj.x5yr21d.xh8yej3':
                        url = str(box.query_selector('a').get_attribute('href'))
                    else:
                        url = str(box.get_attribute('href'))

                    result.append(
                        VideoModel(url=url,
                                   name=None,
                                   date=None))

            for elem in result:
                url = elem.url
                page.goto(url)
                page.wait_for_selector('.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs', timeout=0)
                elem.name = page.query_selector('.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs').text_content()
                elem.date = page.query_selector('.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv.xo1l8bm').query_selector('span').text_content()

        return result

    def show_login_dialog(self, hosting, form, title='login', login='', password='', can_relogin=False):
        self.login_form = LoginForm(form, hosting, self, 2, get_str('enter_login'), get_str('enter_pas'), title=title, username_val=login, password_val=password, relogin=can_relogin)
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=False, use_user_agent_arg=True)
            page = context.new_page()
            page.goto('https://facebook.com')
            page.type('input[name=email]', login)
            page.type('input[name=pass]', password)
            page.keyboard.press('Enter')

            page.wait_for_selector('.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.xzsf02u.x1rg5ohu', timeout=0)
            return page.context.cookies()

    def validate_url_by_account(self, url: str, account) -> int:
        with sync_playwright() as p:
            translator = Translator()

            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(url, wait_until='load', timeout=0)

            try:
                page.wait_for_selector('.xsgj6o6.xw3qccf.x1xmf6yo.x1w6jkce.xusnbm3', timeout=1_000)
            except:
                try:
                    page.wait_for_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.x13a6bvl.x6s0dn4.xozqiw3.x1q0g3np.xcud41i.x139jcc6.x4vbgl9.x1rdy4ex', timeout=1_000)
                except:
                    pass

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

            if switch_item is not None:
                if translator.translate(switch_item.text_content()).text == 'Switch Now' or translator.translate(switch_item.text_content()).text == 'Toggle':
                    switch_item.click()

            page_item = None

            if switch_item is not None:
                page.wait_for_load_state('domcontentloaded', timeout=0)
                page.wait_for_selector('.xsgj6o6.xw3qccf.x1xmf6yo.x187ir9o.xihhdvq', timeout=120_000, state='attached')
                time.sleep(3)
                items = page.query_selector_all('.xsgj6o6.xw3qccf.x1xmf6yo.x187ir9o.xihhdvq')
                for item in items:
                    if item is not None and item.text_content() is not None and translator.translate(item.text_content()).text == 'Edit':
                        page_item = item

            if user_item is None and group_item is None and page_item is None:
                return False
            else:
                return True

    def upload_video(self, account, file_path, name, description, destination=None, table_item: QTableWidgetItem = None):
        with sync_playwright() as p:
            if table_item is not None:
                table_item.setText(get_str('preparing'))
            context = self.new_context(p=p, headless=StateService.settings.debug_browser is False, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto(destination, wait_until='domcontentloaded', timeout=0)

            is_group = False
            page.wait_for_selector('[role="main"]')

            switch_but = None

            if destination.__contains__('groups'):
                with page.expect_file_chooser() as fc_info:
                    page.wait_for_selector('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')
                    page.query_selector_all('.x3nfvp2.x1c4vz4f.x2lah0s.x1emribx')[1].click()
                    is_group = True
            else:
                switch_but = page.query_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xeuugli.xamitd3.x1sxyh0.xurb0ha.x10b6aqq.x1yrsyyn')

                if switch_but is not None:
                    page.click(selector='.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xeuugli.xamitd3.x1sxyh0.xurb0ha.x10b6aqq.x1yrsyyn', timeout=0)

                page.wait_for_selector('[data-pagelet="ProfileComposer"]', timeout=0)
                page.wait_for_selector('.x6s0dn4.x78zum5.xl56j7k.x1rfph6h.x6ikm8r.x10wlt62', timeout=0)
                time.sleep(5)
                page.query_selector_all('.x6s0dn4.x78zum5.xl56j7k.x1rfph6h.x6ikm8r.x10wlt62')[1].click(timeout=0)

                with page.expect_file_chooser() as fc_info:
                    page.wait_for_selector('.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x5yr21d', timeout=0)
                    page.click(selector='.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x5yr21d', timeout=0)
            if table_item is not None:
                table_item.setText(get_str('uploading'))

            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            if table_item is not None:
                table_item.setText(get_str('ending'))

            if is_group is False:
                if switch_but is not None:
                    try:
                        page.wait_for_selector('.x6s0dn4.x1n51wo8.x78zum5.xdt5ytf.x5yr21d.xl56j7k.x1n2onr6', timeout=20_000)
                        page.query_selector_all('.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.xi112ho.x17zwfj4.x585lrc.x1403ito.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xn6708d.x1ye3gou.x1qhmfi1.x1fq8qgq')[0].click()
                    except:
                        pass

                    page.click('.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3.notranslate')
                    page.wait_for_selector('.x6s0dn4.x9f619.x78zum5.x1qughib.x1pi30zi.x1swvt13.xyamay9.xh8yej3', timeout=0)
                    but1 = page.query_selector('.x6s0dn4.x9f619.x78zum5.x1qughib.x1pi30zi.x1swvt13.xyamay9.xh8yej3')
                else:
                    page.click('.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3.notranslate')
                    page.wait_for_selector('.x6s0dn4.x9f619.x78zum5.x1qughib.x1pi30zi.x1swvt13.xyamay9.xh8yej3', timeout=0)
                    page.query_selector('.x6s0dn4.x9f619.x78zum5.x1qughib.x1pi30zi.x1swvt13.xyamay9.xh8yej3').wait_for_selector('.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x1ey2m1c.xds687c.xg01cxk.x47corl.x10l6tqk.x17qophe.x13vifvy.x1ebt8du.x19991ni.x1dhq9h', timeout=0)
                    but1 = page.query_selector('.x6s0dn4.x9f619.x78zum5.x1qughib.x1pi30zi.x1swvt13.xyamay9.xh8yej3').query_selector('.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x1ey2m1c.xds687c.xg01cxk.x47corl.x10l6tqk.x17qophe.x13vifvy.x1ebt8du.x19991ni.x1dhq9h')
            else:
                page.wait_for_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.x1qughib.x1qjc9v5.xozqiw3.x1q0g3np.x1pi30zi.x1swvt13.xyamay9.xcud41i.x139jcc6.x4vbgl9.x1rdy4ex', timeout=0)
                page.query_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.x1qughib.x1qjc9v5.xozqiw3.x1q0g3np.x1pi30zi.x1swvt13.xyamay9.xcud41i.x139jcc6.x4vbgl9.x1rdy4ex').wait_for_selector('.x6s0dn4.x78zum5.xl56j7k.x1608yet.xljgi0e.x1e0frkt', timeout=0)
                but1 = page.query_selector('.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.x1qughib.x1qjc9v5.xozqiw3.x1q0g3np.x1pi30zi.x1swvt13.xyamay9.xcud41i.x139jcc6.x4vbgl9.x1rdy4ex').query_selector('.x6s0dn4.x78zum5.xl56j7k.x1608yet.xljgi0e.x1e0frkt')

            page.keyboard.type(name)

            if switch_but is not None:
                page.wait_for_selector('.x117nqv4.x1sln4lm.xexx8yu.x10l6tqk.xh8yej3.x14ctfv', timeout=0)

                while page.query_selector('.x117nqv4.x1sln4lm.xexx8yu.x10l6tqk.xh8yej3.x14ctfv').text_content().strip() != '100%':
                    time.sleep(2)

            but1.click()
            time.sleep(3)

            while page.query_selector('.always-enable-animations.x1c74tu6.x1u6ievf.xa4qsjk.xuxiujg.x1bndym7.x1pb3rhs') is not None:
                time.sleep(3)

    def check_auth(self, account) -> bool:
        with sync_playwright() as p:
            context = self.new_context(p=p, headless=True, use_user_agent_arg=True)
            context.add_cookies(account.auth)
            page = context.new_page()
            page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=0)

            return page.query_selector('[data-testid="royal_login_form"]') is None

    def need_to_be_uploaded_to_special_source(self) -> bool:
        return True
