import enum

from service.videohosting_service.YoutubeService import YoutubeService
from service.videohosting_service.TikTokService import TikTokService
from service.videohosting_service.VKService import
from service.videohosting_service.InstagramService import InstagramService
from service.videohosting_service.InstagramService import InstagramService
from service.videohosting_service.InstagramService import InstagramService
from service.videohosting_service.InstagramService import InstagramService
from service.videohosting_service.InstagramService import InstagramService
from service.videohosting_service.InstagramService import InstagramService


class Hosting(enum.Enum):
    Youtube = YoutubeService()
    TikTok = TikTokService()
    Instagram = InstagramService()
    Facebook = 'Facebook'
    YandexDzen = 'Яндекс Дзен'
    VK = 'Вконтакте'
    OK = 'Одноклассники'
    Rutube = 'Rutube'
    DTube = 'D.Tube'
    Telegram = 'Telegram'