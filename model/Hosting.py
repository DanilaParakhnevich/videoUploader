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
    Youtube = [YoutubeService(), False]#ga
    TikTok = [TikTokService(), True]#ga
    Instagram = [InstagramService(), False]#ga
    Facebook = [FacebookService(), True]#ga
    YandexDzen = [YandexDzenService(), False]#ga
    VK = [VKService(), True]#ga
    OK = [OKService(), True]#ga
    Rutube = [RutubeService(), False]#ga
    DTube = [DTubeService(), False]#ga
    Telegram = [TelegramService(), True]#g!a
