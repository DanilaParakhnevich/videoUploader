from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from instascrape import Instascraper
from datetime import datetime


class InstagramService(VideohostingService):

    url = 'https://www.instagram.com/'

    def get_videos_by_link(self, link):
        with Instascraper() as insta:
            posts = insta.profile(link.replace(self.url, '').replace('/', '')).timeline_posts()
            result = list()
            for post in posts:
                result.append(VideoModel(post.url, post.caption, str(datetime.fromtimestamp(post.created_time).strftime('%Y-%m-%d %H:%M:%S'))))
        return result
