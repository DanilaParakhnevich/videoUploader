from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from yt_dlp import YoutubeDL


class YandexDzenService(VideohostingService):
    extract_info_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'logger': False,
        "extract_flat": True,
    }

    def get_videos_by_link(self, link):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            info = ydl.extract_info(link)
            for item in info['entries']:
                result.append(VideoModel(item['url'], item['title'], None))
            print(info)
        return result

    def show_login_dialog(self, hosting, url, form):

        return list()

    def login(self, url, login, password):
        pass
