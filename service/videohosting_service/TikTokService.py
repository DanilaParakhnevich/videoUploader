from TikTokAPI import TikTokAPI

from service.videohosting_service.VideohostingService import VideohostingService


class TikTokService(VideohostingService):


    def get_videos_by_link(self, link, account=None):
        return list()

    def show_login_dialog(self, hosting, form):
        return list()

    def login(self, login, password):
        pass

if __name__ == '__main__':
    cookie = {
        "s_v_web_id": "verify_lgs7vr0c_4GPnBm0z_Nj6H_4ZIY_BDJ1_WqvKJ4NBuhHI",
        "tt_webid": "1%7C_2HnX3yqpGkyZOQhrfjH3XSIyKP7yBrnecuLRCePuUk%7C1682184070%7Ceb5cf524c952f3cf91095a555c66e52c0abe959d442dd7cb849f8e67f8599ef2"
    }

    api = TikTokAPI(cookie=cookie)
    api.getTrending(count=30)