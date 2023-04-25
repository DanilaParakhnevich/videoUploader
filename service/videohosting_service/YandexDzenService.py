from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from yt_dlp import YoutubeDL
import json
from playwright.sync_api import sync_playwright


class YandexDzenService(VideohostingService):
    extract_info_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'logger': False,
        "extract_flat": True,
    }

    def get_videos_by_link(self, link, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context()
                page = context.new_page()
                info = ydl.extract_info(link)
                for item in info['entries']:
                    page.goto(item['url'].split('?')[0])
                    response = json.loads(
                        page.content().split('<script type="application/ld+json" nonce="">')[1].split('</script')[0])

                    result.append(VideoModel(item['url'], response['name'], response['uploadDate']))
        return result

    def show_login_dialog(self, hosting, form):

        return list()

    def login(self, login, password):
        pass
