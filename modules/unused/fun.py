from discord.ext import commands
import discord, aiohttp, random, config, datetime
from io import BytesIO
import os
import rethinkdb as r
import nekobot
from .utils.hastebin import post as haste

key = config.weeb
auth = {"Authorization": "Wolke " + key}

food = [
    "🍪",
    "🍣",
    "🍟",
    "🍕",
    "🍚",
    "🍇",
    "🍓",
    "🍔",
    "🍰",
    "🍄",
    "🍡",
    "🍛",
    "🌵",
    "🍜",
    "🌽",
    "🍶",
    "🍆",
    "🍌",
    "🍬",
    "🍋",
    "🍹",
    "🍝",
    "🍮",
    "🎂",
    "🍏",
    "🍈",
    "🍠",
    "☕",
    "🍺",
    "🍷",
    "🍥",
    "🥚",
    "🍨",
    "🍭",
    "🍊",
    "🍉",
    "🍞",
    "🍍",
    "🍘",
    "🍧"
]

class Fun:
    """Fun Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.nekobot = nekobot.Client()

    async def __has_voted(self, user:int):
        if await r.table("votes").get(str(user)).run(self.bot.r_conn):
            return True
        else:
            return False

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def catgirlmeme(self, ctx):
        """Everything is a dollar not spent on genetically engendering catgirls for domestic ownership"""
        if ctx.channel.is_nsfw():
            async with aiohttp.ClientSession() as cs:
                async with cs.get("https://nekos.life/api/v2/img/gecg") as r:
                    res = await r.json()
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=res["url"])
            em.set_footer(text="nekos.life owo")
            await ctx.send(embed=em)
        else:
            return await ctx.send("Use this in an nsfw channel just to make sure")

    async def get_image(self, effect:str, ctx:commands.Context, user:discord.Member):
        await ctx.trigger_typing()
        if not user:
            message = ctx.message
            if not len(message.attachments) >= 1:
                def check(m):
                    return m.channel == message.channel and m.author == message.author
                try:
                    await ctx.send("Please send an image to %s." % effect)
                    x = await self.bot.wait_for('message', check=check, timeout=13)
                except Exception:
                    return await ctx.send("Timed out...")
                if not len(x.attachments) >= 1:
                    return await ctx.send("No images found.")
                img = x.attachments[0].url
            else:
                img = message.attachments[0].url
        else:
            img = user.avatar_url_as(format="png")
        return img

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def caption(self, ctx, user:discord.Member=None):
        """Caption an image"""
        img = await self.get_image("caption", ctx, user)
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
            async with aiohttp.ClientSession() as cs:
                async with cs.post(url, headers=headers, json=payload) as r:
                    data = await r.text()
            em = discord.Embed(color=0xDEADBF, title=str(data))
            em.set_image(url=img)
            await ctx.send(embed=em)
        except:
            await ctx.send("Failed to get data.")

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def blurpify(self, ctx, user:discord.Member=None):
        """Either blurpify a user or attach an image."""
        img = await self.get_image("blurpify", ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.blurpify(img)))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def phcomment(self, ctx, *, comment:str):
        """PronHub Comment Image"""
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=phcomment"
                              f"&image={ctx.author.avatar_url_as(format='png')}"
                              f"&text={comment}&username={ctx.author.name}") as r:
                res = await r.json()
        if not res["success"]:
            return await ctx.send("**Failed to successfully get image.**")
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res["message"]))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def toxicity(self, ctx, *, text:str):
        """Get text toxicity levels"""
        try:
            API_KEY = "AIzaSyAc49LROgPF9IEiLDavWqwb2z8UndUUbcM"
            url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=" + API_KEY
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
            async with aiohttp.ClientSession() as cs:
                async with cs.post(url, json=analyze_request) as r:
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
    async def weebify(self, ctx, *, text:str):
        """Weebify Text"""
        try:
            key = config.idiotic_api
            async with aiohttp.ClientSession(headers={"Authorization": key}) as cs:
                async with cs.get(f'https://dev.anidiots.guide/text/owoify?text={text}') as r:
                    res = await r.json()
            await ctx.send(res['text'])
        except:
            await ctx.send("Failed to connect.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def achievement(self, ctx, *, achievement:str):
        """Achievement Generator"""
        await ctx.trigger_typing()
        try:
            url = f"https://dev.anidiots.guide/generators/achievement?avatar={ctx.message.author.avatar_url_as(format='png')}&text={achievement}"
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url, headers={"Authorization": config.idiotic_api}) as r:
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
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tweet(self, ctx, username:str, *, text:str):
        """Tweet as someone."""
        await ctx.trigger_typing()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.tweet(username, text)))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def nichijou(self, ctx, text:str):
        """Tweet as someone."""
        await ctx.trigger_typing()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.nichijou(text)))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def threats(self, ctx, user:discord.Member):
        img = await self.get_image("threatify", ctx, user)
        if not isinstance(img, str):
            return img
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.threats(img)))

    @commands.command(aliases=['pillow'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bodypillow(self, ctx, user: discord.Member):
        """Bodypillow someone"""
        img = await self.get_image("bodypillow", ctx, user)
        if not isinstance(img, str):
            return img
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekobot.xyz/api/imagegen?type=bodypillow&url=%s" % img) as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res["message"]))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def baguette(self, ctx, user:discord.Member):
        """:^)"""
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.baguette(user.avatar_url_as(format="png"))))

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def deepfry(self, ctx, user:discord.Member=None):
        """Deepfry a user"""
        img = await self.get_image("deepfry", ctx, user)
        if not isinstance(img, str):
            return img
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.deepfry(img)))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def clyde(self, ctx, *, text : str):
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.clyde(text)))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def joke(self, ctx):
        """Sends a Joke OwO"""
        async with aiohttp.ClientSession(headers={"Accept": "application/json"}) as cs:
            async with cs.get('https://icanhazdadjoke.com/') as r:
                res = await r.json()
                e = discord.Embed(color=0xDEADBF, description=f"**{res['joke']}**")\
                    .set_thumbnail(url="https://vignette.wikia.nocookie.net/2b2t8261/images/e/ed/LUL.png")
                await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bigletter(self, ctx, *, text:str):
        """Big Letter Generator"""
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://nekobot.xyz/api/text?type=bigletter&text="+text) as r:
                res = await r.json()
        return await ctx.send(res["message"])

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Ship OwO"""
        if user2 is None:
            user2 = ctx.message.author

        await ctx.trigger_typing()
        ranxd = random.randint(1, 2)
        if ranxd == 1:
            if not os.path.isfile(f"data/ship/mode1-{user1.id}-{user2.id}.png"):
                async with aiohttp.ClientSession() as session:
                    async with session.post('https://api.weeb.sh/auto-image/love-ship',
                                            headers={'Authorization': f'Wolke {config.weeb}'},
                                            data={'targetOne': user1.avatar_url, 'targetTwo': user2.avatar_url}) as response:
                        t = await response.read()
                        with open(f"data/ship/mode1{user1.id}-{user2.id}.png", "wb") as f:
                            f.write(t)
                        score = random.randint(0, 100)
                        filled_progbar = round(score / 100 * 10)
                        counter_ = '█' * filled_progbar + '‍ ‍' * (10 - filled_progbar)

                        self_length = len(user1.name)
                        first_length = round(self_length / 2)
                        first_half = user1.name[0:first_length]
                        usr_length = len(user2.name)
                        second_length = round(usr_length / 2)
                        second_half = user2.name[second_length:]
                        finalName = first_half + second_half
                        e = discord.Embed(color=0xDEADBF, title=f'{user1.name} ❤ {user2.name}', description=f"**Love %**\n"
                                                                                            f"`{counter_}` **{score}%**\n\n"
                                                                                            f"{finalName}")
            await ctx.send(file=discord.File(fp=f'data/ship/mode1{user1.id}-{user2.id}.png'),
                           embed=e.set_image(url=f'attachment://mode1{user1.id}-{user2.id}.png'))
        else:
            user2url = user2.avatar_url
            user1url = user1.avatar_url

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
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://nekobot.xyz/api/imagegen?type=ship&user1={user1url}&user2={user2url}") as r:
                    res = await r.json()
            e = discord.Embed(color=0xDEADBF, title=f'{user1.name} ❤ {user2.name}', description=f"**Love %**\n"
                                                                                                f"`{counter_}` **{score}%**\n\n"
                                                                                                f"{finalName}")
            if not res['success']:
                return await ctx.send(
                    embed=discord.Embed(color=0xDEADBF, description="Failed to successfully get the image."))
            await ctx.send(content="{}".format(finalName),
                           embed=e.set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def shitpost(self, ctx):
        """Shitpost ofc"""
        if not ctx.channel.is_nsfw:
            return await ctx.send("Use this in an nsfw channel.")

        await ctx.trigger_typing()
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get("https://www.reddit.com/r/copypasta/hot.json?sort=hot") as r:
                    res = await r.json()

            data = random.choice(res["data"]["children"])["data"]
            em = discord.Embed(color=0xDEADBF, title=data["title"], description=data["selftext"], url=data["url"])
            em.set_footer(text="👍 - %s upvotes" % data["ups"])
            await ctx.send(embed=em)

        except Exception as e:
            await ctx.send("Failed to get data, %s" % e)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def captcha(self, ctx, user: discord.Member):
        """Captcha a User OWO"""
        await ctx.trigger_typing()
        url = user.avatar_url_as(format="png")
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.captcha(url, user.name)))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def whowouldwin(self, ctx:commands.Context, user1: discord.Member, user2: discord.Member = None):
        """Who would win"""
        await ctx.trigger_typing()
        if user2 is None:
            user2 = ctx.message.author
        user1url = user1.avatar_url
        user2url = user2.avatar_url
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.whowouldwin(user1url, user2url)))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def awooify(self, ctx, user: discord.Member=None):
        """AwWOOOOO"""
        img = await self.get_image("awooify", ctx, user)
        if not isinstance(img, str):
            return img
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.awooify(img)))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def duck(self, ctx):
        """Gets a duck image /shrug"""
        self.bot.counter['duck'] += 1
        url = "https://api.random-d.uk/random"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        em = discord.Embed(color=0xDEADBF)
        await ctx.send(embed=em.set_image(url=res['url']).set_footer(text=f"Ducks sent since last restart: {self.bot.counter['duck']}"))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def changemymind(self, ctx, *, text:str):
        if await self.__has_voted(ctx.author.id):
            await ctx.trigger_typing()
            await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.changemymind(text)))
        else:
            em = discord.Embed(color=0xDEADBF, description="https://discordbots.org/bot/nekobot/vote", title="owo whats this")
            return await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def magik(self, ctx, user:discord.Member=None):
        """Magikify a member"""
        img = await self.get_image("magik", ctx, user)
        if not isinstance(img, str):
            return img
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.magik(img)))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def owoify(self, ctx, *, text:str = None):
        try:
            if text is None:
                return await ctx.send("oopsie whoopsie you made a fucky wucky, you gave me no text to owoify")
            else:
                text = text.replace(' ', '%20')
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://nekos.life/api/v2/owoify?text={text}") as r:
                    res = await r.json()
            try:
                em = discord.Embed(color=0xDEADBF, description=f"{res['owo']}", title="OwOified Text")
                await ctx.send(embed=em)
            except:
                return await ctx.send("Failed to get the OwOified Text or you input is over 100 characters.")
        except:
            await ctx.send("Failed to owoify.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lizard(self, ctx):
        """Get a lizard owo"""
        url = "https://nekos.life/api/v2/img/lizard"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['url']))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        """Get a dank meme OwO"""
        sub = ["dankmemes", "animemes"] #Add more?
        url = f'https://api.imgur.com/3/gallery/r/{random.choice(sub)}/hot/{random.randint(1, 5)}'
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
        js = random.choice(res['data'])
        if js['nsfw'] or js['is_ad']:
            while True:
                js = random.choice(res['data'])
                if not js['nsfw'] or not js['is_ad']:
                    break
        embed = discord.Embed(color=0xDEADBF,
                              description=f"**{js['title']}**")
        embed.set_image(url=js['link'])
        time = datetime.datetime.fromtimestamp(int(js['datetime'])).strftime('%Y-%m-%d %H:%M')
        embed.set_footer(text=f"Posted on {time}")

        await ctx.send(embed=embed)


    @commands.command(aliases=["dick", "penis"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dong(self, ctx, *, user : discord.Member):
        """Detects user's dong length"""
        state = random.getstate()
        random.seed(user.id)
        dong = "8{}D".format("=" * random.randint(0, 30))
        random.setstate(state)
        em = discord.Embed(title="{}'s Dong Size".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def jpeg(self, ctx, user : discord.Member = None):
        """OwO Whats This"""
        img = await self.get_image("jpeg", ctx, user)
        if not isinstance(img, str):
            return img
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=await self.nekobot.jpeg(img)))

    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gif(self, ctx, *keywords):
        """Retrieves first search result from giphy"""
        keywords = "+".join(keywords)
        url = ("http://api.giphy.com/v1/gifs/search?&api_key={}&q={}&rating=g"
               "".format(config.giphy_key, keywords))

        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
                if res["data"]:
                    await ctx.send(res["data"][0]["url"])
                else:
                    await ctx.send("No results found.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cat(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=animal_cat') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dog(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=animal_dog') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def feed(self, ctx, user : discord.Member):
        if user == ctx.message.author:
            await ctx.send(f"-- {ctx.message.author.mention} eats {random.choice(food)} --")
        else:
            await ctx.send(f"-- Forces {random.choice(food)} down {user.name}'s throat --")

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def iphonex(self, ctx:commands.Context, *, url: str):
        """Generate an iPhone X Image"""
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=iphonex&url={url}") as r:
                res = await r.json()
        if not res['success']:
            return await ctx.send("**Error generating image with that url.**")
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def kannagen(self, ctx, *, text:str):
        """Generate Kanna"""
        await ctx.trigger_typing()
        url = f"https://nekobot.xyz/api/imagegen?type=kannagen&text={text}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        if not res['success']:
            return await ctx.send(embed=discord.Embed(color=0xDEADBF, description="Failed to successfully get the image."))
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command(aliases=['fite', 'rust'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def fight(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Fite sum1"""
        if user2 == None:
            user2 = ctx.message.author

        map = "https://vignette.wikia.nocookie.net/callofduty/images/3/33/Rust.jpg"
        em = discord.Embed(color=0xDEADBF,
                           title="Intense Rust 1v1")
        em.set_image(url=map)
        em.add_field(name=f"Round | {user1.name} vs {user2.name}",
                     value=f"***pew pew*** {random.choice([user1.name, user2.name])} got the first hit and won OwO")
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Fun(bot))
