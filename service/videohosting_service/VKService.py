from service.videohosting_service.VideohostingService import VideohostingService
from service.StateService import StateService
from gui.widgets.LoginForm import LoginForm
from gui.widgets.AuthenticationConfirmationForm import AuthenticationConfirmationForm
import vk_api

class VKService(VideohostingService):

    form = None
    state_service = StateService()

    def get_videos_by_link(self, link):
        channel = self.state_service.get_channel_by_url(link)

        # access token https://ru.stackoverflow.com/questions/288901/%D0%9F%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE-vkontakte-api
        return list()

    def show_login_dialog(self, hosting, url, form):
        self.login_form = LoginForm(form, hosting, url, self)
        self.login_form.exec_()

    def login(self, url, login, password):
        vk_session = vk_api.VkApi(login=login,
                                  password=password,
                                  auth_handler=self.handle_auth,
                                  scope=vk_api.VkUserPermissions.OFFLINE)
        vk_session.auth(reauth=True)
        vk_session.too_many_rps_handler()
        return vk_session.token

    def handle_auth(self):
        form = AuthenticationConfirmationForm(self.login_form, '1111111')
        form.exec_()
        return form.code_edit.text(), True
