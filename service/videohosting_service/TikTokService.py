from TikTokAPI import TikTokAPI

from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright
from time import sleep

class TikTokService(VideohostingService):


    def get_videos_by_link(self, link, account=None):
        return list()

    def show_login_dialog(self, hosting, form):
        return list()

    def login(self, login, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://www.tiktok.com/login')
            page.wait_for_selector(selector='.elwz89c90')

            page.screenshot(path="s1.jpg")
            return page.context.cookies()

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://www.tiktok.com/login')
        # page.wait_for_selector(selector='.elwz89c90', timeout=0)
        sleep(100000000)
        page.screenshot(path="s1.jpg")