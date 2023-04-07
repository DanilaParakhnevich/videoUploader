from service.videohosting_service.VideohostingService import VideohostingService
from model.VideoModel import VideoModel
from instascrape import Instascraper
from datetime import datetime


class FacebookService(VideohostingService):

    def get_videos_by_link(self, link):
        # access token https://developers.facebook.com/docs/video-api/guides/get-videos/
        return list()