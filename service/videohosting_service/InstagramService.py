from datetime import datetime, time

from PyQt5.QtWidgets import QTableWidgetItem
from googletrans import Translator

from service.LocalizationService import get_str
from service.StateService import StateService
from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from gui.widgets.LoginForm import LoginForm
from playwright.sync_api import sync_playwright
import re


class InstagramService(VideohostingService):

    def __init__(self):
        self.video_regex = 'https:\/\/www.instagram.com\/p\/.*\/'
        self.channel_regex = 'https:\/\/www.instagram.com\/.*'
        self.upload_video_formats = list(['mp4', 'mov'])
        self.duration_restriction = 1
        self.size_restriction = 100
        self.title_size_restriction = 2_200
        self.min_title_size = 0

    def get_videos_by_url(self, url, account=None):
        result = list()

        with sync_playwright() as p:
            context = self.new_context(p, True, True)

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            page.goto(url, wait_until='networkidle', timeout=0)
            page.wait_for_selector('[role="tablist"]', timeout=40_000)
            self.scroll_page_to_the_bottom(page=page)
            stream_boxes = page.locator("//a[contains(@class,'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd')]")
            translator = Translator()

            for box in stream_boxes.element_handles():
                svg = box.query_selector('svg')

                if svg is not None:
                    aria_label = svg.get_attribute('aria-label')

                    if translator.translate(aria_label).text == 'Clip' or translator.translate(
                            aria_label).text == 'Video':

                        aagu = box.query_selector('._aagu')
                        not_parsed_date = aagu.query_selector('img').get_property('alt')
                        if re.search(' on (.*).', str(not_parsed_date)) is not None:
                            date = re.search(' on (.*).', str(aagu.query_selector('img').get_property('alt'))).group(1)
                        else:
                            date = get_str('no_info')

                        result.append(
                            VideoModel(url=f'https://www.instagram.com{box.get_attribute("href")}',
                                       name=get_str('no_info'),
                                       date=date))

            return result

    def show_login_dialog(self, hosting, form):
        self.login_form = LoginForm(form, hosting, self, 2, 'Введите логин', 'Введите пароль')
        self.login_form.exec_()

        return self.login_form.account

    def login(self, login, password):
        with sync_playwright() as p:
            context = self.new_context(p, False, True)
            page = context.new_page()
            page.goto('https://www.instagram.com/')
            page.type('input[name="username"]', login)
            page.type('input[name="password"]', password)
            page.click('._acap')
            page.wait_for_selector('._aauo', timeout=0)

            return page.context.cookies()

    def need_to_pass_channel_after_login(self):
        return False

    def check_auth(self, account) -> bool:
        for auth in account.auth:
            if auth['name'] == 'sessionid':
                if datetime.utcfromtimestamp(auth['expires']) > datetime.now():
                    return True
                else:
                    return False
        return False

    def upload_video(self, account, file_path, name, description, destination=None,
                     table_item: QTableWidgetItem = None):
        if table_item is not None:
            table_item.setText(get_str('preparing'))

        with sync_playwright() as p:
            context = self.new_context(p=p, headless=StateService.settings.debug_browser is False)

            if account is not None:
                context.add_cookies(account.auth)

            page = context.new_page()
            page.goto('https://www.instagram.com/', timeout=0)

            try:
                page.wait_for_selector('._a9-v', timeout=20_000)
                page.click('._a9--._a9_1')
            except:
                pass

            page.wait_for_selector('.x9f619.x3nfvp2.xr9ek0c.xjpr12u.xo237n4.x6pnmvc.x7nr27j.x12dmmrz.xz9dl7a.xn6708d.xsag5q8.x1ye3gou.x80pfx3.x159b3zp.x1dn74xm.xif99yt.x172qv1o.x10djquj.x1lhsz42.xzauu7c.xdoji71.x1dejxi8.x9k3k5o.xs3sg5q.x11hdxyr.x12ldp4w.x1wj20lx.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c', timeout=0)
            page.query_selector_all('.x9f619.x3nfvp2.xr9ek0c.xjpr12u.xo237n4.x6pnmvc.x7nr27j.x12dmmrz.xz9dl7a.xn6708d.xsag5q8.x1ye3gou.x80pfx3.x159b3zp.x1dn74xm.xif99yt.x172qv1o.x10djquj.x1lhsz42.xzauu7c.xdoji71.x1dejxi8.x9k3k5o.xs3sg5q.x11hdxyr.x12ldp4w.x1wj20lx.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c')[6].click()

            page.wait_for_selector('._acan._acap._acas._aj1-', timeout=0)

            with page.expect_file_chooser() as fc_info:
                page.click(
                    selector='._acan._acap._acas._aj1-',
                    timeout=0)
            if table_item is not None:
                table_item.setText(get_str('uploading'))
            file_chooser = fc_info.value
            file_chooser.set_files(file_path, timeout=0)

            if table_item is not None:
                table_item.setText(get_str('ending'))

            page.wait_for_selector('._ac7b._ac7d', timeout=0)

            try:
                page.wait_for_selector('._ag4f', timeout=20_000)
                page.click('._acan._acap._acaq._acas._acav._aj1-')
            except:
                pass

            page.click('._ac7b._ac7d')
            page.wait_for_selector('._ac7b._ac7d')
            page.click('._ac7b._ac7d')

            page.click('.x6s0dn4.x78zum5.x1n2onr6.xh8yej3')
            page.keyboard.type(name)

            page.click('._ac7b._ac7d')

            page.wait_for_selector('.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.x1ms8i2q.xo1l8bm.x5n08af.x2b8uid.x4zkp8e.xw06pyt.x10wh9bi.x1wdrske.x8viiok.x18hxmgj', timeout=0)
