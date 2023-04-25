from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from yt_dlp import YoutubeDL
from datetime import datetime


class FacebookService(VideohostingService):

    def get_videos_by_link(self, link, account=None):
        # access token https://developers.facebook.com/docs/video-api/guides/get-videos/
        return list()

    def show_login_dialog(self, hosting, form):

        return list()

    def login(self, login, password):
        pass


if __name__ == '__main__':
    extract_info_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'logger': False,
        "extract_flat": True,
    }

    result = list()

    with YoutubeDL(extract_info_opts) as ydl:
        info = ydl.extract_info('https://www.facebook.com/people/Marwah-Sopa/pfbid02GnRkup21d7ZsiR3nuhdLvBipYV9DCd1bKA3aNBUhURQRteTbdbcLGX4SK7frFKBFl/')
        for item in info['entries']:
            result.append(VideoModel(item['url'], item['title']
                                     , datetime.fromtimestamp(item['timestamp']).__str__()))
