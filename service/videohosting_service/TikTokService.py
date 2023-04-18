import time
from TikTokApi import TikTokApi
from playwright.sync_api import sync_playwright
from yt_dlp import YoutubeDL

from service.videohosting_service.VideohostingService import VideohostingService


class TikTokService(VideohostingService):

    url = 'https://www.tiktok.com/@'
    #https://scrapfly.io/blog/web-scraping-with-playwright-and-python/#scrolling-and-infinite-pagination



    def get_videos_by_link(self, link, account=None):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            page.goto(link)
            # wait for content to fully load:
            page.wait_for_selector(".tiktok-1qb12g8-DivThreeColumnContainer")

            # loop scrolling last element into view until no more new elements are created
            stream_boxes = None
            while True:
                stream_boxes = page.locator("//div[contains(@class,'tw-tower')]/div[@data-target]")
                stream_boxes.element_handles()[-1].scroll_into_view_if_needed()
                items_on_page = len(stream_boxes.element_handles())
                page.wait_for_timeout(2_000)  # give some time for new items to load
                items_on_page_after_scroll = len(stream_boxes.element_handles())
                if items_on_page_after_scroll > items_on_page:
                    continue  # more items loaded - keep scrolling
                else:
                    break  # no more items - break scrolling loop
            # parse data:
            parsed = []

    def show_login_dialog(self, hosting, form):

        return list()

    def login(self, login, password):
        pass


if __name__ == "__main__":
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto("https://www.tiktok.com/@0udanovskiy2")
        # wait for content to fully load:
        page.wait_for_selector(".tiktok-1qb12g8-DivThreeColumnContainer")

        # loop scrolling last element into view until no more new elements are created
        stream_boxes = None
        while True:
            stream_boxes = page.locator("//div[contains(@class,'tiktok-yvmafn-DivVideoFeedV2')]/div[contains(@class,'tiktok-x6y88p-DivItemContainerV2')]")
            stream_boxes.element_handles()[-1].scroll_into_view_if_needed()
            items_on_page = len(stream_boxes.element_handles())
            page.wait_for_timeout(2_000)  # give some time for new items to load
            items_on_page_after_scroll = len(stream_boxes.element_handles())
            if items_on_page_after_scroll > items_on_page:
                continue  # more items loaded - keep scrolling
            else:
                break  # no more items - break scrolling loop
        # parse data:

        parsed = []