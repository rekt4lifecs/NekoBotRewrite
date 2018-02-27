from discord.ext import commands
import discord, aiohttp, requests, random, config, datetime, asyncio
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup as bs

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

    @commands.command(pass_context=True)
    async def ship(self, ctx, user : discord.Member, user2 : discord.Member):
        """Ship someone UwU"""
        user2url = user2.avatar_url
        user1url = user.avatar_url
        #Yes ik I use requests when this is async gitgud ;-;
        r1 = requests.get(user1url)
        r2 = requests.get(user2url)
        img = Image.open("data/ship/ship.jpg")
        user1img = Image.open(BytesIO(r1.content))
        user2img = Image.open(BytesIO(r2.content))

        user1img = user1img.resize((int(250), int(250)))
        user2img = user2img.resize((int(225), int(225)))
        img.paste(user1img, (280, 210))
        img.paste(user2img, (620, 130))

        self_length = len(user.name)
        first_length = round(self_length / 2)
        first_half = user.name[0:first_length]
        usr_length = len(user2.name)
        second_length = round(usr_length / 2)
        second_half = user2.name[second_length:]
        finalName = first_half + second_half

        img.save(f"data/ship/ship-{user.id}.png")
        await ctx.send(file=discord.File(f'data/ship/ship-{user.id}.png'), content="{}".format(finalName))

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def shitpost(self, ctx):
        """Shitpost ofc"""
        shitpost = config.shitpost
        await ctx.send(embed=discord.Embed(description=random.choice(shitpost),
                                           color=0xDEADBF))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
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
    async def penis(self, ctx, *, user : discord.Member):
        """Detects user's penis length"""
        state = random.getstate()
        random.seed(user.id)
        dong = "8{}D".format("=" * random.randint(0, 30))
        random.setstate(state)
        em = discord.Embed(title="{}'s Dick Size".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command()
    async def vagina(self, ctx, *, user: discord.Member):
        """Detects user's vaginas depth"""
        state = random.getstate()
        random.seed(user.id)
        dong = "{} Meters Deep".format(str(random.randint(0, 30)))
        random.setstate(state)
        em = discord.Embed(title="{}'s Puss Depth".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    async def jpeg(self, ctx, user : discord.Member):
        """OwO Whats This"""
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
        await ctx.send(file=discord.File("data/JPEG.jpg"))

    @commands.command()
    async def isnowillegal(self, ctx, legal : str):
        """Make Stuff Illegal!"""
        legal = legal.upper()
        url = "https://storage.googleapis.com/is-now-illegal.appspot.com/gifs/" + legal +".gif"
        em = discord.Embed(title="{} is now Illegal!".format(legal))
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command(pass_context=True, no_pm=True)
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
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random.cat/meow') as r:
                res = await r.json()
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=res['file'])
        await ctx.send(embed=em)

    @commands.command()
    async def feed(self, ctx, user : discord.Member):
        if user == ctx.message.author:
            await ctx.send(f"-- {ctx.message.author.mention} eats {random.choice(food)} --")
        else:
            await ctx.send(f"-- Forces {random.choice(food)} down {user.name}'s throat --")

    @commands.command()
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

    @commands.command()
    async def boom(self, ctx):
        """BOOM"""
        await ctx.message.add_reaction("🅱")
        await ctx.message.add_reaction("🇴")
        await ctx.message.add_reaction("💥")
        await ctx.message.add_reaction("🇲")

def setup(bot):
    bot.add_cog(Fun(bot))