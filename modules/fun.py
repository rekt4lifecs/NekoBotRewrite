from discord.ext import commands
import discord, aiohttp, requests, random, config, datetime, asyncio, youtube_dl, base64, hashlib, textwrap, uuid
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageOps, ImageFilter
from bs4 import BeautifulSoup as bs

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, ytdl.extract_info, url)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

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

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def food(self, ctx):
        """Grabs Random Food Recipes"""
        url = "https://www.themealdb.com/api/json/v1/1/random.php"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
                res = res['meals'][0]
        meal = res['strMeal']
        meal_type = res['strCategory']
        instructions = res['strInstructions']
        thumb = res['strMealThumb']

        ingredient1 = res['strIngredient1']
        ingredient2 = res['strIngredient2']
        ingredient3 = res['strIngredient3']
        ingredient4 = res['strIngredient4']
        ingredient5 = res['strIngredient5']
        ingredient6 = res['strIngredient6']
        ingredient7 = res['strIngredient7']
        ingredient8 = res['strIngredient8']
        ingredient9 = res['strIngredient9']
        ingredient10 = res['strIngredient10']
        ingredient11 = res['strIngredient11']
        ingredient12 = res['strIngredient12']
        ingredient13 = res['strIngredient13']
        ingredient14 = res['strIngredient14']
        ingredient15 = res['strIngredient15']
        ingredient16 = res['strIngredient16']
        ingredient17 = res['strIngredient17']
        ingredient18 = res['strIngredient18']
        ingredient19 = res['strIngredient19']
        ingredient20 = res['strIngredient20']

        e = discord.Embed(color=0xDEADBF,
                          title=f"{meal} | {meal_type}",
                          description=instructions)
        e.add_field(name="Ingredients:", value=f"{ingredient1} {ingredient2} {ingredient3} {ingredient4} {ingredient5}"
                                               f" {ingredient6} {ingredient7} {ingredient8} {ingredient9} {ingredient10}"
                                               f" {ingredient11} {ingredient12} {ingredient13} {ingredient14} {ingredient15}"
                                               f" {ingredient16} {ingredient17} {ingredient18} {ingredient19} {ingredient20}")

        e.set_image(url=thumb)

        try:
            await ctx.send(embed=e)
        except:
            await ctx.send("There was an error. Please try again.")

    @commands.command(name="b64", aliases=['b64encode', 'base64encode'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def base_encode(self, ctx, *, encode_to: str):
        """Encode with Base64"""
        try:
            encoded = base64.b64encode(encode_to.encode())
            await ctx.send(embed=discord.Embed(color=0xDEADBF, title=f"{encode_to}",
                                               description=f"```\n{encoded}\n```"))
        except Exception as e:
            await ctx.send(f"Could not encode.\n`{e}`")

    @commands.command(name="md5")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def md_five(self, ctx, *, encode_to: str):
        """Encode with Base64"""
        try:
            encoded = hashlib.md5(encode_to.encode('utf-8')).hexdigest()
            await ctx.send(embed=discord.Embed(color=0xDEADBF, title=f"{encode_to}",
                                               description=f"```\n{encoded}\n```"))
        except Exception as e:
            await ctx.send(f"Could not encode.\n`{e}`")

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def clyde(self, ctx, *, text : str = None):
        if text is None:
            text = "ReKT is best bot maker"

        img = Image.open("data/clyde.png")

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("data/fonts/Whitney.ttf", 20)

        draw.text((120, 80), text, (255, 255, 255), font=font)
        num = random.randint(1, 10)
        img.save(f"data/clyde{num}.png")

        await ctx.send(file=discord.File(f"data/clyde{num}.png"))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def monkaS(self, ctx):
        try:
            emoji = self.bot.get_emoji(385481793853194240)
            await ctx.message.add_reaction(emoji)
        except:
            pass

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def gachiBASS(self, ctx, song : str = None):
        try:
            emoji = self.bot.get_emoji(393591272021164042)
            await ctx.message.add_reaction(emoji)
            emoji = self.bot.get_emoji(393591279067463682)
            await ctx.message.add_reaction(emoji)
            emoji = self.bot.get_emoji(393591271773700101)
            await ctx.message.add_reaction(emoji)
            emoji = self.bot.get_emoji(393591644764504064)
            await ctx.message.add_reaction(emoji)
        except:
            pass

        if song is None:
            song = random.choice(["https://www.youtube.com/watch?v=J1Q0rgkFrA0",
                                  "https://www.youtube.com/watch?v=J9poH0Q4k6A",
                                  "https://www.youtube.com/watch?v=roqUWBibQ_o",
                                  "https://www.youtube.com/watch?v=bwPLwX9aluY",
                                  "https://www.youtube.com/watch?v=y3YHnkCDnKY",
                                  "https://www.youtube.com/watch?v=gq3JxkARYRk",
                                  "https://www.youtube.com/watch?v=kOCxHu_F5xo",
                                  "https://www.youtube.com/watch?v=cPJNEGqf_jw"])

        if ctx.voice_client is None:
            try:
                if ctx.author.voice.channel:
                        await ctx.author.voice.channel.connect()
                else:
                    return
            except:
                return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        player = await YTDLSource.from_url(song, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        ctx.voice_client.source.volume = 100
        await ctx.send('Now playing: **`{}`**'.format(player.title))

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def circulation(self, ctx):
        try:
            emoji = self.bot.get_emoji(388367971371712512)
            await ctx.message.add_reaction(emoji)
        except:
            pass

        song = "https://www.youtube.com/watch?v=uKxyLmbOc0Q"

        if ctx.voice_client is None:
            try:
                if ctx.author.voice.channel:
                        await ctx.author.voice.channel.connect()
                else:
                    return
            except:
                return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        player = await YTDLSource.from_url(song, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        ctx.voice_client.source.volume = 150
        await ctx.send('Now playing: **`{}`**'.format(player.title))

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
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Ship OwO"""
        if user2 is None:
            user2 = ctx.message.author

        await ctx.trigger_typing()
        ranxd = random.randint(1, 2)
        if ranxd == 1:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.weeb.sh/auto-image/love-ship',
                                        headers={'Authorization': f'Wolke {config.weeb}'},
                                        data={'targetOne': user1.avatar_url, 'targetTwo': user2.avatar_url}) as response:
                    t = await response.read()
                    numx = random.randint(1, 5)
                    with open(f"ship{numx}.png", "wb") as f:
                        f.write(t)
                    rnd = random.randint(1, 20)
                    l1 = (len(user1.name))
                    l2 = (len(user2.name))
                    score = 100 - (l1 * l2) - rnd
                    filled_progbar = round(score / 100 * 10)
                    counter_ = '█' * filled_progbar + '‍ ‍' * (10 - filled_progbar)

                    self_length = len(user1.name)
                    first_length = round(self_length / 2)
                    first_half = user1.name[0:first_length]
                    usr_length = len(user2.name)
                    second_length = round(usr_length / 2)
                    second_half = user2.name[second_length:]
                    if user1 == 178189410871803904:
                        counter_ = "#################"
                        score = 100
                    finalName = first_half + second_half
                    e = discord.Embed(color=0xDEADBF, title=f'{user1.name} ❤ {user2.name}', description=f"**Love %**\n"
                                                                                        f"`{counter_}` **{score}%**\n\n"
                                                                                        f"{finalName}")
                    await ctx.send(file=discord.File(fp=f'ship{numx}.png'), embed=e.set_image(url=f'attachment://ship{numx}.png'))
        elif ranxd == 2:
            user2url = user2.avatar_url
            user1url = user1.avatar_url
            # Yes ik I use requests when this is async gitgud ;-;
            r1 = requests.get(user1url)
            r2 = requests.get(user2url)
            img = Image.open("data/ship/ship.jpg")
            user1img = Image.open(BytesIO(r1.content))
            user2img = Image.open(BytesIO(r2.content))

            user1img = user1img.resize((int(250), int(250)))
            user2img = user2img.resize((int(225), int(225)))
            img.paste(user1img, (280, 210))
            img.paste(user2img, (620, 130))

            self_length = len(user1.name)
            first_length = round(self_length / 2)
            first_half = user1.name[0:first_length]
            usr_length = len(user2.name)
            second_length = round(usr_length / 2)
            second_half = user2.name[second_length:]
            finalName = first_half + second_half

            img.save(f"data/ship/ship-{user1.id}.png")
            rnd = random.randint(1, 20)
            l1 = (len(user1.name))
            l2 = (len(user2.name))
            score = 100 - (l1 * l2) - rnd
            filled_progbar = round(score / 100 * 10)
            counter_ = '█' * filled_progbar + '‍ ‍' * (10 - filled_progbar)
            e = discord.Embed(color=0xDEADBF, title=f'{user1.name} ❤ {user2.name}', description=f"**Love %**\n"
                                                                                                f"`{counter_}` **{score}%**\n\n"
                                                                                                f"{finalName}")
            await ctx.send(file=discord.File(f'data/ship/ship-{user1.id}.png'), content="{}".format(finalName),
                           embed=e.set_image(url=f'attachment://ship-{user1.id}.png'))

    @commands.command()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def shitpost(self, ctx):
        """Shitpost ofc"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://37.59.36.62:10000/shitpost") as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(description=random.choice(res['msg']),
                                           color=0xDEADBF))

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def meme(self, ctx):
        """Get a dank meme OwO"""
        # NoSteal kthx
        sub = "dankmemes" #Add more?
        data = config.imgur._get_imgur(self, sub)['data']
        js = random.choice(data)
        if js['nsfw'] or js['is_ad'] == True:
            while True:
                print("Had to loop meme")
                js = random.choice(data)
                if js['nsfw'] or js['is_ad'] == False:
                    break
        embed = discord.Embed(color=0xDEADBF,
                              description=f"**{js['title']}**")
        embed.set_image(url=js['link'])
        time = datetime.datetime.fromtimestamp(int(js['datetime'])).strftime('%Y-%m-%d %H:%M')
        embed.set_footer(text=f"Posted on {time}")

        await ctx.send(embed=embed)


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def penis(self, ctx, *, user : discord.Member):
        """Detects user's penis length"""
        if not ctx.message.channel.is_nsfw(): return
        state = random.getstate()
        random.seed(user.id)
        dong = "8{}D".format("=" * random.randint(0, 30))
        random.setstate(state)
        em = discord.Embed(title="{}'s Dick Size".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vagina(self, ctx, *, user: discord.Member):
        """Detects user's vaginas depth"""
        if not ctx.message.channel.is_nsfw(): return
        state = random.getstate()
        random.seed(user.id)
        dong = "{} Meters Deep".format(str(random.randint(0, 30)))
        random.setstate(state)
        em = discord.Embed(title="{}'s Puss Depth".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def jpeg(self, ctx, user : discord.Member = None):
        """OwO Whats This"""
        if user is None:
            user = ctx.message.author
        try:
            url = user.avatar_url
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert('RGB')
        except:
            await ctx.send('Error getting image!')
            return
        final = BytesIO()
        img.save('data/JPEG.jpg', quality=1)
        final.seek(0)
        await ctx.send(file=discord.File(fp='data/JPEG.jpg'))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def isnowillegal(self, ctx, legal : str):
        """Make Stuff Illegal!"""
        legal = legal.upper()
        url = "https://storage.googleapis.com/is-now-illegal.appspot.com/gifs/" + legal +".gif"
        em = discord.Embed(title="{} is now Illegal!".format(legal))
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gif(self, ctx, *keywords):
        """Retrieves first search result from giphy"""
        if keywords:
            keywords = "+".join(keywords)
        else:
            await self.bot.send_cmd_help(ctx)
            return

        url = ("http://api.giphy.com/v1/gifs/search?&api_key={}&q={}&rating=g"
               "".format(config.giphy.key, keywords))

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
    async def bitconnect(self, ctx):
        videos = ["https://www.youtube.com/watch?v=d1oZ6P8ZBoM", "https://www.youtube.com/watch?v=CJe0rWOP4fE",
                  "https://www.youtube.com/watch?v=A8M70M7tzTI", "https://www.youtube.com/watch?v=lc2-ImMRMC8",
                  "https://www.youtube.com/watch?v=GLQAXo0xonI", "https://www.youtube.com/watch?v=9wlDhciUDD0",
                  "https://www.youtube.com/watch?v=vhyAREaWfyU", "https://www.youtube.com/watch?v=Ii_D-Fcks_A",
                  "https://www.youtube.com/watch?v=lsgvcCnztJ4", "https://www.youtube.com/watch?v=PDiSLXcAU3U",
                  "https://www.youtube.com/watch?v=d4a88-IhAVw", "https://www.youtube.com/watch?v=8tOFoEP-2f4",
                  "https://www.youtube.com/watch?v=e5nyQmaq4k4", "https://www.youtube.com/watch?v=upejO2mFqX0",
                  "https://www.youtube.com/watch?v=aPD9Mj1OWo4", "https://www.youtube.com/watch?v=Dy7RnUOmNcQ",
                  "https://www.youtube.com/watch?v=d4a88-IhAVw", "https://www.youtube.com/watch?v=vabXXkZjKiw",
                  "https://www.youtube.com/watch?v=W2GKSZdPgrY", "https://www.youtube.com/watch?v=axKTFLkFzDM",
                  "https://www.youtube.com/watch?v=FRA9FZSZKlg"]
        await ctx.send(random.choice(videos))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def feed(self, ctx, user : discord.Member):
        if user == ctx.message.author:
            await ctx.send(f"-- {ctx.message.author.mention} eats {random.choice(food)} --")
        else:
            await ctx.send(f"-- Forces {random.choice(food)} down {user.name}'s throat --")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lovecalculator(self, ctx, user1 : discord.Member, user2 : discord.Member = None):
        """Love Calculator"""
        if user2 == None:
            user2 = ctx.message.author
        rnd = random.randint(1, 20)
        l1 = (len(user1.name))
        l2 = (len(user2.name))
        score = 100 - (l1 * l2) - rnd
        if score > 40:
            heart = "❤"
        else:
            heart = "💔"
        embed = discord.Embed(color=0xDEADBF,
                              title="Love Calculator",
                              description=f"{user1.name} {heart} {user2.name} = {score}%")
        await ctx.send(embed=embed)

    @commands.command(name='disconnect')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vc_disconnect(self, ctx):
        """Disconnect from vc"""
        try:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from voice channel")
        except:
            await ctx.send("Bot is not in a voice channel.")

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def iphonex(self, ctx, *, url: str):
        """Generate an iPhone X Image"""
        bg = Image.new('RGBA', (360, 722), (0, 0, 0, 0))
        img = Image.open("data/iphonex.png").convert('RGBA')
        try:
            url = requests.get(url)
            url = Image.open(BytesIO(url.content)).convert('RGBA').resize((315, 682))
        except:
            return await ctx.send("**There was an error receiving that image url.**")
        bg.alpha_composite(url, (20, 20))
        bg.alpha_composite(img, (0, 0))

        num = uuid.uuid4()
        bg.save(f'data/iphone/{num}.png')

        await ctx.send(file=discord.File(f'data/iphone/{num}.png'),
                       embed=discord.Embed(color=0xDEADBF).set_image(url=f'attachment://{num}.png'))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def kannagen(self, ctx, *, text:str):
        """Generate Kanna"""
        img = Image.open('data/kannagen.jpg').convert('RGBA').rotate(12)
        hand = Image.open('data/hand.png').rotate(12)

        text = '\n'.join(textwrap.wrap(text, 13))

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("data/fonts/arial.ttf", 15)

        draw.text((35, 37), text, (0, 0, 0), font)

        img.alpha_composite(hand)

        img = img.rotate(-8)

        img.save("kanna.png")

        await ctx.send(file=discord.File("kanna.png"))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def butts(self, ctx):
        await ctx.send("ლ(́◉◞౪◟◉‵ლ)")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def boom(self, ctx):
        """BOOM"""
        await ctx.message.add_reaction("🅱")
        await ctx.message.add_reaction("🇴")
        await ctx.message.add_reaction("💥")
        await ctx.message.add_reaction("🇲")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rude(self, ctx):
        """RUDE"""
        await ctx.message.add_reaction("🇷")
        await ctx.message.add_reaction("🇺")
        await ctx.message.add_reaction("🇩")
        await ctx.message.add_reaction("🇪")

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
