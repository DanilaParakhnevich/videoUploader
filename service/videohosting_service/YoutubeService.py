from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
import scrapetube


class YoutubeService(VideohostingService):

    url = 'https://www.youtube.com/'

    def get_videos_by_link(self, link):
        c = scrapetube.get_channel(channel_url=link)
        result = list()
        for video in c:
            link = f'{self.url}{{video["navigationEndpoint"]["commandMetadata"]["web/CommandMetadata"]}}'
            result.append(VideoModel(link, video['title']['runs'][0]['text'], video['publishedTimeText']['simpleText']))
        return result

    def show_login_dialog(self, hosting, url, form):

        return list()

    def login(self, url, login, password):
        pass
