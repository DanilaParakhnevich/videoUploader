from abc import ABC
import abc
class VideohostingService(ABC):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_videos_by_link(self, link, account=None):
        return list()

    @abc.abstractmethod
    def show_login_dialog(self, hosting, form):
        raise NotImplementedError()

    @abc.abstractmethod
    def login(self, login, password):
        raise NotImplementedError()
