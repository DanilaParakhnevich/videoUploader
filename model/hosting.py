import enum

from service.videohosting_service.YoutubeService import YoutubeService
from service.videohosting_service.TikTokService import TikTokService
from service.videohosting_service.VKService import VKService
from service.videohosting_service.YandexDzenService import YandexDzenService
from service.videohosting_service.FacebookService import FacebookService
from service.videohosting_service.TelegramService import TelegramService
from service.videohosting_service.OKService import OKService
from service.videohosting_service.DTubeService import DTubeService
from service.videohosting_service.RutubeService import RutubeService
from service.videohosting_service.InstagramService import InstagramService


# Этот класс хранит все доступные видеохостинги с необходимыми
# данными в качестве значений для работы с ними:
# (Объект соответсвующего сервиса, Обязательна ли авторизация для выборки данных)
class Hosting(enum.Enum):
    Youtube = [YoutubeService(), False]#done
    TikTok = [TikTokService(), True]
    Instagram = [InstagramService(), False]#done
    Facebook = [FacebookService(), True]
    YandexDzen = [YandexDzenService(), True]#done
    VK = [VKService(), True]
    OK = [OKService(), True]
    Rutube = [RutubeService(), True]
    DTube = [DTubeService(), True]
    Telegram = [TelegramService(), True]
