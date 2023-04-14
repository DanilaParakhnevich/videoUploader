from abc import ABC
import abc
class VideohostingService(ABC):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_videos_by_link(self, link):
        return list()

    @abc.abstractmethod
    def login(self, login, password, form):
        raise NotImplementedError()
