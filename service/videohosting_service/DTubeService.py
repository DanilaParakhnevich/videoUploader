from service.videohosting_service.VideohostingService import VideohostingService


class DTubeService(VideohostingService):

    def get_videos_by_link(self, link):
        # scrapping or try to use youtube-dl
        return list()

    def show_login_dialog(self, hosting, url, form):

        return list()

    def login(self, url, login, password):
        pass
