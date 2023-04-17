from service.videohosting_service.VideohostingService import VideohostingService


class RutubeService(VideohostingService):

    def get_videos_by_link(self, link):
        # access token https://ru.stackoverflow.com/questions/288901/%D0%9F%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE-vkontakte-api
        return list()

    def show_login_dialog(self, hosting, url, form):

        return list()

    def login(self, url, login, password):
        pass
