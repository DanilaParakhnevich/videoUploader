from service.videohosting_service.VideohostingService import VideohostingService


class TelegramService(VideohostingService):

    def get_videos_by_link(self, link):
        # need to authorize, use API (https://www.youtube.com/watch?v=aU1p-F7gDo4)
        return list()

    def show_login_dialog(self, hosting, url, form):

        return list()

    def login(self, url, login, password):
        pass
