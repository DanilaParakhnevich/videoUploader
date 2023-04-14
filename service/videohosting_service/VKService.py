from service.videohosting_service.VideohostingService import VideohostingService
import vk_api

class VKService(VideohostingService):

    form = None

    def get_videos_by_link(self, link):
        # access token https://ru.stackoverflow.com/questions/288901/%D0%9F%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE-vkontakte-api
        return list()

    def login(self, login, password, form):

        self.form = form

        vk_session = vk_api.VkApi('+375292306154', 'Molotok.5074344', auth_handler=self.handle_auth,
                                  scope=vk_api.VkUserPermissions.OFFLINE)
        vk_session.auth()

        return vk_session.token

    def handle_auth(self):
        code = input()
        return code, True
