from service.videohosting_service.VideohostingService import VideohostingService
from yt_dlp import YoutubeDL
from model.VideoModel import VideoModel
from datetime import datetime

class DTubeService(VideohostingService):

    extract_info_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'logger': False,
        "extract_flat": True,
    }

    def get_videos_by_link(self, link, account=None):
        result = list()

        with YoutubeDL(self.extract_info_opts) as ydl:
            info = ydl.extract_info(link)
            for item in info['entries']:
                result.append(VideoModel(f'https://d.tube/#!/v/{item["id"]}', item['title'],
                                         datetime.fromtimestamp(item['timestamp']).__str__()))

        return result

    def show_login_dialog(self, hosting, form):
        #https://github.com/yvetal/dtube-steem-video-upload/blob/master/dtube_handler.py
        return list()

    def login(self, login, password):
        pass