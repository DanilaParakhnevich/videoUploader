import time
from tiktokpy import TikTokPy

from service.videohosting_service.VideohostingService import VideohostingService
from time import sleep


class TikTokService(VideohostingService):

    url = 'https://www.tiktok.com/@'

    async def get_videos_by_link(self, link):
        # todo что-нибудь придумать с тт

        async with TikTokPy() as bot:
            # 😏 getting user's feed
            user_feed_items = await bot.user_feed(username='justinbieber', amount=5)

            for item in user_feed_items:
                # 🎧 get music title, cover, link, author name..
                print("Music title: ", item.music.title)
                # #️⃣ print all tag's title of video
                print([tag.title for tag in item.challenges])
                # 📈 check all video stats
                print("Comments: ", item.stats.comments)
                print("Plays: ", item.stats.plays)
                print("Shares: ", item.stats.shares)
                print("Likes: ", item.stats.likes)

            return user_feed_items
