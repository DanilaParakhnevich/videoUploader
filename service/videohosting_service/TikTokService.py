from service.videohosting_service.VideohostingService import VideohostingService
from playwright.sync_api import sync_playwright


class TikTokService(VideohostingService):


    def get_videos_by_link(self, link, account=None):
        return list()

    def show_login_dialog(self, hosting, form):
        return list()

    def login(self, login, password):
        CHROMIUM_ARGS = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--disable-blink-features=AutomationControlled'
        ]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=CHROMIUM_ARGS, ignore_default_args=['--enable-automation'])
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://www.tiktok.com/login')
            page.wait_for_selector(selector='#main-content-homepage_hot', timeout=0)
