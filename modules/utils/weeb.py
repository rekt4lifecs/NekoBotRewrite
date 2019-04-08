import aiohttp
import logging
from io import BytesIO

log = logging.getLogger()

class Weeb:

    def __init__(self, token: str, bot, user_agent: str = "NekoBot/4.2.0"):
        self.user_agent = user_agent
        self.bot = bot
        self.headers = {
            "Authorization": "Wolke " + token,
            "User-Agent": self.user_agent
        }

        self.endpoint = "https://api.weeb.sh/images/"

    async def get_dominant_color(self, url: str):
        try:
            name = url.rpartition("/")[2]
            data = await self.bot.redis.get(name)
            if data:
                return int(data.decode("utf8"))
            else:
                return 14593471
        except Exception as e:
            log.error("Failed to get dominant color, %s" % e)
            return 14593471

    async def types(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "types") as r:
                if r.status == 200:
                    res = await r.json()
                    data = res["types"]
                else:
                    data = []

        return data

    async def awoo(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=awoo") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def bang(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=bang") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def blush(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=blush") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def clagwimoth(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=clagwimoth") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def cry(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=cry") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def cuddle(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=cuddle") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def dance(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=dance") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def hug(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=hug") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def insult(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=insult") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def jojo(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=jojo") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def kiss(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=kiss") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def lewd(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=lewd") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def lick(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=lick") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def megumin(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=megumin") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def neko(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=neko") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def nom(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=nom") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def owo(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=owo") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def pat(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=pat") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def poke(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=poke") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def pout(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=pout") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def rem(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=rem") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def shrug(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=shrug") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def slap(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=slap") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def sleepy(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=sleepy") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def smile(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=smile") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def teehee(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=teehee") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def smug(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=smug") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def stare(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=stare") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def thumbsup(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=thumbsup") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def triggered(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=triggered") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def wag(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=wag") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def waifu_insult(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=waifu_insult") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def wasted(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=wasted") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def sumfuk(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=sumfuk") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def dab(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=dab") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def tickle(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=tickle") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def highfive(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=highfive") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def banghead(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=banghead") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def bite(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=bite") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def discord_memes(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=discord_memes") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def nani(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=nani") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def initial_d(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=initial_d") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def delet_this(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=delet_this") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def poi(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=poi") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def thinking(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=thinking") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def greet(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=greet") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def punch(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=punch") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def handholding(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=handholding") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def kemonomimi(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=kemonomimi") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def trap(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=trap") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def deredere(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=deredere") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def dog(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=animal_dog") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def cat(self):
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.get(self.endpoint + "random?type=animal_cat") as r:
                res = await r.json()

        url = res["url"]
        color = await self.get_dominant_color(url)
        return color, url

    async def waifu_insult_gen(self, avatar: str):
        body = {
            "avatar": avatar
        }
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.post("https://api.weeb.sh/auto-image/waifu-insult", data=body) as r:
                res = await r.read()

        return BytesIO(res)

    async def loveship_gen(self, avatar1: str, avatar2: str):
        body = {
            "targetOne": avatar1,
            "targetTwo": avatar2
        }
        async with aiohttp.ClientSession(headers=self.headers) as cs:
            async with cs.post("https://api.weeb.sh/auto-image/love-ship", data=body) as r:
                res = await r.read()

        return BytesIO(res)