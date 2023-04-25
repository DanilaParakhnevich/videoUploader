from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from yt_dlp import YoutubeDL
from datetime import datetime

class RutubeService(VideohostingService):

    extract_info_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'logger': False,
        "extract_flat": True,
    }

    def get_videos_by_link(self, link, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            info = ydl.extract_info('https://rutube.ru/channel/25933729/videos/')
            for item in info['entries']:
                result.append(VideoModel(item['url'], item['title']
                                         , datetime.fromtimestamp(item['timestamp']).__str__()))

        return result

    def show_login_dialog(self, hosting, form):

        return list()

    def login(self, login, password):
        pass
