from service.videohosting_service.VideohostingService import VideohostingService


class OKService(VideohostingService):

    def get_videos_by_link(self, link):
        # https://stackoverflow.com/questions/61261777/how-to-extract-video-urls-and-titles-from-ok-ru-video-using-the-cli or hard api or scrapping...
        return list()

    def show_login_dialog(self, hosting, url, form):

        return list()

    def login(self, url, login, password):
        pass
