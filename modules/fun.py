from discord.ext import commands
import discord
import aiohttp

import config
from io import BytesIO
import random
import datetime

auth = {"Authorization": "Wolke " + config.weeb}

monika_faces = [x for x in "abcdefghijklmnopqr"]
natsuki_faces = [x for x in "abcdefghijklmnopqrstuvwxyz"]
natsuki_faces.extend(["1t", "2bt", "2bta", "2btb", "2btc", "2btd", "2bte", "2btf", "2btg", "2bth", "2bti",
                      "2t", "2ta", "2tb", "2tc", "2td", "2te", "2tf", "2tg", "2th", "2ti"])
sayori_faces = [x for x in "abcdefghijklmnopqrstuvwxy"]
yuri_faces = [x for x in "abcdefghijklmnopqrstuvwx"]
yuri_faces.extend(["y1", "y2", "y3", "y4", "y5", "y6", "y7"])
ddlc_items = {
    "body": {
        "monika": [ "1", "2" ],
        "natsuki": [ "1b", "1", "2b", "2"],
        "yuri": ["1b", "1", "2b", "2"],
        "sayori": ["1b", "1", "2b", "2"]
    },
    "face": {
        "monika": monika_faces,
        "natsuki": natsuki_faces,
        "yuri": yuri_faces,
        "sayori": sayori_faces
    }
}

ddlc_get_character = {
    "y": "yuri",
    "n": "natsuki",
    "m": "monika",
    "s": "sayori"
}

m_offets = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1)
]

m_numbers = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]

class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.session.close()
        del self.session

    async def __get_image(self, ctx, user=None):
        if user:
            if user.is_avatar_animated():
                return str(user.avatar_url_as(format="gif"))
            else:
                return str(user.avatar_url_as(format="png"))

        await ctx.trigger_typing()

        message = ctx.message

        if len(message.attachments) > 0:
            return message.attachments[0].url

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            await ctx.send("Send me an image!")
            x = await self.bot.wait_for('message', check=check, timeout=15)
        except:
            return await ctx.send("Timed out...")

        if not len(x.attachments) >= 1:
            return await ctx.send("No images found.")

        return x.attachments[0].url

    def __embed_json(self, data, key="message"):
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=data[key])
        return em

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def animeface(self, ctx, user: discord.Member = None):
        """Detect anime faces in an image"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=animeface&image=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def caption(self, ctx, user: discord.Member = None):
        """Caption an image"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "Content": img,
            "Type": "CaptionRequest"
        }
        url = "https://captionbot.azurewebsites.net/api/messages"
        try:
            async with self.session.post(url, headers=headers, json=payload) as r:
                data = await r.text()
            em = discord.Embed(color=0xDEADBF, title=str(data))
            em.set_image(url=img)
            await ctx.send(embed=em)
        except:
            await ctx.send("Failed to get data.")

    @commands.command(aliases=["ddlcgen"])
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def ddlc(self, ctx, character: str, text: commands.clean_content(fix_channel_mentions=True, escape_markdown=True),
                   background: str = "class", body: str = "1", face: str = "a"):
        """DDLC Gen hahayes
        Place your text in "quotations" for more than 1 character.
        Example:
            n!ddlc yuri "OwO whats this" club 2 h

        List of bodies for each character:
            Monika: 1, 2
            Natsuki: 1b, 1, 2b, 2
            Sayori: 1b, 1, 2b, 2
            Yuri: 1b, 1, 2b, 2

        List of faces for each character:
            Monika: a to r
            Natsuki: a to z and more such as 1t, 2btf, 2th
            Sayori: a to y
            Yuri: a to w and y1 to y7

        Backgrounds:
            bedroom, class, closet, club, corridor, house, kitchen, residential, sayori_bedroom"""
        characters = ["yuri", "monika", "sayori", "natsuki", "y", "m", "s", "n"]
        character = character.lower()
        if character not in characters:
            return await ctx.send("Not a valid character.")
        if len(text) >= 140:
            return await ctx.send("Text too long ;w;")
        background = background.lower()
        backgrounds = ["bedroom", "class", "closet", "club", "corridor", "house", "kitchen", "residential", "sayori_bedroom"]
        if background not in backgrounds:
            return await ctx.send("Not a valid background must be one of " + ", ".join(["`%s`" % x for x in backgrounds]))
        if len(character) == 1:
            character = ddlc_get_character.get(character)
        if not body in ddlc_items.get("body").get(character):
            return await ctx.send("Not a valid body")
        if not face in ddlc_items.get("face").get(character):
            return await ctx.send("Not a valid face")

        await ctx.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=ddlc"
                          "&character=%s"
                          "&background=%s"
                          "&body=%s"
                          "&face=%s"
                          "&text=%s" % (character, background, body, face, text)) as r:
            res = await r.json()
        em = discord.Embed(color=0xffe6f4).set_image(url=res["message"])
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def blurpify(self, ctx, user:discord.Member=None):
        """Blurpify something!"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=blurpify&image=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def phcomment(self, ctx, *, comment: str):
        """PronHub Comment Image"""
        await ctx.trigger_typing()
        async with self.session.get(f"https://nekobot.xyz/api/imagegen?type=phcomment"
                          f"&image={ctx.author.avatar_url_as(format='png')}"
                          f"&text={comment}&username={ctx.author.name}") as r:
            res = await r.json()
        if not res["success"]:
            return await ctx.send("**Failed to successfully get image.**")
        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def toxicity(self, ctx, *, text: str):
        """Get text toxicity levels"""
        try:
            url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=" + config.googlekey
            analyze_request = {
                'comment': {'text': f'{text}'},
                'requestedAttributes': {'TOXICITY': {},
                                        'SEVERE_TOXICITY': {},
                                        'SPAM': {},
                                        'UNSUBSTANTIAL': {},
                                        'OBSCENE': {},
                                        'INFLAMMATORY': {},
                                        'INCOHERENT': {}}
            }
            async with self.session.post(url, json=analyze_request) as r:
                response = await r.json()
            em = discord.Embed(color=0xDEADBF, title="Toxicity Levels")
            em.add_field(name="Toxicity",
                         value=f"{round(float(response['attributeScores']['TOXICITY']['summaryScore']['value'])*100)}%")
            em.add_field(name="Severe Toxicity",
                         value=f"{round(float(response['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value'])*100)}%")
            em.add_field(name="Spam",
                         value=f"{round(float(response['attributeScores']['SPAM']['summaryScore']['value'])*100)}%")
            em.add_field(name="Unsubstantial",
                         value=f"{round(float(response['attributeScores']['UNSUBSTANTIAL']['summaryScore']['value'])*100)}%")
            em.add_field(name="Obscene",
                         value=f"{round(float(response['attributeScores']['OBSCENE']['summaryScore']['value'])*100)}%")
            em.add_field(name="Inflammatory",
                         value=f"{round(float(response['attributeScores']['INFLAMMATORY']['summaryScore']['value'])*100)}%")
            em.add_field(name="Incoherent",
                         value=f"{round(float(response['attributeScores']['INCOHERENT']['summaryScore']['value'])*100)}%")
            await ctx.send(embed=em)
        except discord.Forbidden:
            pass
        except:
            await ctx.send("Error getting data.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weebify(self, ctx, *, text: str):
        """Weebify Text"""
        try:
            key = config.idiotic_api
            async with self.session.get(f'https://dev.anidiots.guide/text/owoify?text={text}', headers={"Authorization": key}) as r:
                res = await r.json()
            await ctx.send(res['text'].replace("@", "@\u200B"))
        except:
            await ctx.send("Failed to connect.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def achievement(self, ctx, *, achievement: str):
        """Achievement Generator"""
        await ctx.trigger_typing()
        try:
            url = f"https://dev.anidiots.guide/generators/achievement?avatar={ctx.author.avatar_url_as(format='png')}&text={achievement}"
            async with self.session.get(url, headers={"Authorization": config.idiotic_api}) as r:
                res = await r.json()
            file = discord.File(BytesIO(bytes(res["data"])), filename="image.png")
            em = discord.Embed(color=0xDEADBF)
            await ctx.send(file=file, embed=em.set_image(url="attachment://image.png"))
            try:
                await ctx.message.delete()
            except:
                pass
        except:
            await ctx.send(f"Failed to get data, `{res['errors'][0]['message']}`")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tweet(self, ctx, username: str, *, text: str):
        """Tweet as someone."""
        await ctx.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=tweet"
                          "&username=%s"
                          "&text=%s" % (username, text,)) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def nichijou(self, ctx, *, text: str):
        if len(text) > 22:
            return await ctx.send("Text too long ;w;")
        await ctx.trigger_typing()
        async with self.session.get("https://i.ode.bz/auto/nichijou?text=%s" % text) as r:
            res = await r.read()

        file = discord.File(fp=BytesIO(res), filename="nichijou.gif")
        await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def threats(self, ctx, user: discord.Member):
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=threats&url=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command(aliases=['pillow'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bodypillow(self, ctx, user: discord.Member):
        """Bodypillow someone"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=bodypillow&url=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def baguette(self, ctx, user: discord.Member):
        """:^)"""
        await ctx.trigger_typing()
        avatar = user.avatar_url_as(format="png")
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=baguette&url=%s" % avatar) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def deepfry(self, ctx, user: discord.Member = None):
        """Deepfry a user"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=deepfry&image=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def clyde(self, ctx, *, text: str):
        await ctx.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=clyde&text=%s" % text) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Ship OwO"""
        if user2 is None:
            user2 = ctx.author

        await ctx.trigger_typing()
        if user1.avatar:
            user1url = "https://cdn.discordapp.com/avatars/%s/%s.png" % (user1.id, user1.avatar,)
        else:
            user1url = "https://cdn.discordapp.com/embed/avatars/1.png"
        if user2.avatar:
            user2url = "https://cdn.discordapp.com/avatars/%s/%s.png" % (user2.id, user2.avatar,)
        else:
            user2url = "https://cdn.discordapp.com/embed/avatars/1.png"

        self_length = len(user1.name)
        first_length = round(self_length / 2)
        first_half = user1.name[0:first_length]
        usr_length = len(user2.name)
        second_length = round(usr_length / 2)
        second_half = user2.name[second_length:]
        finalName = first_half + second_half

        score = random.randint(0, 100)
        filled_progbar = round(score / 100 * 10)
        counter_ = '█' * filled_progbar + '‍ ‍' * (10 - filled_progbar)

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=ship&user1=%s&user2=%s" % (user1url, user2url,)) as r:
            res = await r.json()

        em = discord.Embed(color=0xDEADBF)
        em.title = "%s ❤ %s" % (user1.name, user2.name,)
        em.description = f"**Love %**\n" \
                         f"`{counter_}` **{score}%**\n\n{finalName}"
        em.set_image(url=res["message"])

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lolice(self, ctx):
        """KNOCK KNOCK KNOCK"""
        await ctx.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=lolice&url=%s" % ctx.author.avatar_url_as(format="png")) as r:
            res = await r.json()
        em = discord.Embed(color=0xDEADBF)
        await ctx.send(embed=em.set_image(url=res["message"]))

    @commands.command()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def fact(self, ctx, *, text: str):
        if len(text) > 165:
            return await ctx.send("Text too long...")
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=fact"
                          "&text=%s" % text) as r:
            res = await r.json()

        await ctx.trigger_typing()
        em = discord.Embed(color=0xDEADBF)
        await ctx.send(embed=em.set_image(url=res["message"]))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def shitpost(self, ctx):
        """Shitpost ofc"""
        if not ctx.channel.is_nsfw:
            return await ctx.send("Use this in an nsfw channel.")

        await ctx.trigger_typing()
        try:
            async with self.session.get("https://www.reddit.com/r/copypasta/hot.json?sort=hot") as r:
                res = await r.json()

            data = random.choice(res["data"]["children"])["data"]
            em = discord.Embed(color=0xDEADBF, title=data["title"], description=data["selftext"], url=data["url"])
            em.set_footer(text="👍 - %s upvotes" % data["ups"])
            await ctx.send(embed=em)

        except Exception as e:
            await ctx.send("Failed to get data, %s" % e)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def captcha(self, ctx, user: discord.Member):
        """Captcha a User OWO"""
        await ctx.trigger_typing()
        url = user.avatar_url_as(format="png")
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=captcha&url=%s&username=%s" % (url, user.name,)) as r:
            res = await r.json()
        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def trash(self, ctx, user: discord.Member):
        """trash smh"""
        await ctx.trigger_typing()
        url = user.avatar_url_as(format="jpg")
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=trash&url=%s" % (url,)) as r:
            res = await r.json()
        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whowouldwin(self, ctx: commands.Context, user1: discord.Member, user2: discord.Member = None):
        """Who would win"""
        await ctx.trigger_typing()
        if user2 is None:
            user2 = ctx.author
        user1url = user1.avatar_url
        user2url = user2.avatar_url

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=whowouldwin&user1=%s&user2=%s" % (user1url, user2url,)) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def awooify(self, ctx, user: discord.Member = None):
        """AwWOOOOO"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=awooify&url=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def changemymind(self, ctx, *, text: str):
        await ctx.trigger_typing()

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=changemymind&text=%s" % text) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def magik(self, ctx, user: discord.Member = None):
        """Magikify a member"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=magik&image=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        """Get a dank meme OwO"""
        sub = ["dankmemes", "animemes"]  # Add more?
        url = f'https://api.imgur.com/3/gallery/r/{random.choice(sub)}/hot/{random.randint(1, 5)}'
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        async with self.session.get(url, headers=headers) as r:
            res = await r.json()
        if res["status"] == 429:
            return await ctx.send("**Ratelimited, try again later.**")
        js = random.choice(res['data'])
        f = False
        if js['nsfw'] or js['is_ad']:
            for x in res["data"]:
                if not js['nsfw'] or not js['is_ad']:
                    js = x
                    f = True
                    break
        else:
            f = js
        if not f:
            return await ctx.send("Nothing found")
        embed = discord.Embed(color=0xDEADBF,
                              description=f"**{js['title']}**")
        embed.set_image(url=js['link'])
        time = datetime.datetime.fromtimestamp(int(js['datetime'])).strftime('%Y-%m-%d %H:%M')
        embed.set_footer(text=f"Posted on {time}")

        await ctx.send(embed=embed)

    @commands.command(aliases=["dick", "penis"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dong(self, ctx, *, user: discord.Member):
        """Detects user's dong length"""
        state = random.getstate()
        random.seed(user.id)
        dong = "8{}D".format("=" * random.randint(0, 30))
        random.setstate(state)
        em = discord.Embed(title="{}'s Dong Size".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def jpeg(self, ctx, user: discord.Member = None):
        """OwO Whats This"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img

        async with self.session.get("https://nekobot.xyz/api/imagegen?type=jpeg&url=%s" % img) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gif(self, ctx, *keywords):
        """Retrieves first search result from giphy"""
        keywords = "+".join(keywords)
        url = ("http://api.giphy.com/v1/gifs/search?&api_key={}&q={}&rating=g"
               "".format(config.giphy_key, keywords))

        async with self.session.get(url) as r:
            res = await r.json()
        if res["data"]:
            await ctx.send(res["data"][0]["url"])
        else:
            await ctx.send("No results found.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cat(self, ctx):
        async with self.session.get('https://api.weeb.sh/images/random?type=animal_cat', headers=auth) as r:
            res = await r.json()
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=res["url"])
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dog(self, ctx):
        async with self.session.get('https://api.weeb.sh/images/random?type=animal_dog', headers=auth) as r:
            res = await r.json()
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=res["url"])
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def iphonex(self, ctx, user:discord.Member=None):
        """Generate an iPhone X Image"""
        img = await self.__get_image(ctx, user)
        if not isinstance(img, str):
            return img
        await ctx.trigger_typing()
        async with self.session.get(f"https://nekobot.xyz/api/imagegen?type=iphonex&url={img}") as r:
            res = await r.json()
        await ctx.send(embed=self.__embed_json(res))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kannagen(self, ctx, *, text: str):
        """Generate Kanna"""
        await ctx.trigger_typing()
        url = f"https://nekobot.xyz/api/imagegen?type=kannagen&text={text}"
        async with self.session.get(url) as r:
            res = await r.json()

        await ctx.send(embed=self.__embed_json(res))

    @commands.command(aliases=['fite', 'rust'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def fight(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Fite sum1"""
        if user2 == None:
            user2 = ctx.author

        win = random.choice([user1, user2])

        if win == user1:
            lose = user2
        else:
            lose = user1

        await ctx.send("%s beat %s!" % (win.mention, lose.mention,))

    @commands.command()
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def minesweeper(self, ctx, size: int = 5):
        size = max(min(size, 8), 2)
        bombs = [[random.randint(0, size - 1), random.randint(0, size - 1)] for x in range(int(size - 1))]
        is_on_board = lambda x, y: 0 <= x < size and 0 <= y < size
        has_bomb = lambda x, y: [i for i in bombs if i[0] == x and i[1] == y]
        message = "**Click to play**:\n"
        for y in range(size):
            for x in range(size):
                tile = "||{}||".format(chr(11036))
                if has_bomb(x, y):
                    tile = "||{}||".format(chr(128163))
                else:
                    count = 0
                    for xmod, ymod in m_offets:
                        if is_on_board(x + xmod, y + ymod) and has_bomb(x + xmod, y + ymod):
                            count += 1
                    if count != 0:
                        tile = "||{}||".format(m_numbers[count - 1])
                message += tile
            message += "\n"
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Fun(bot))
