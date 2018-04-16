from discord.ext import commands
import discord, random, aiohttp, requests
from bs4 import BeautifulSoup as bs
from collections import Counter
import config
import aiomysql
import json

class NSFW:
    """NSFW Commands OwO"""

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()

    async def execute(self, query: str, isSelect: bool = False, fetchAll: bool = False, commit: bool = False):
        connection = await aiomysql.connect(host='localhost', port=3306,
                                              user='root', password=config.dbpass,
                                              db='nekobot')
        async with connection.cursor() as db:
            await db.execute(query)
            if isSelect:
                if fetchAll:
                    values = await db.fetchall()
                else:
                    values = await db.fetchone()
            if commit:
                await connection.commit()
        connection.close()
        if isSelect:
            return values

    @commands.command()
    @commands.is_owner()
    async def hasvoted(self, ctx):
        votes = await self.execute("SELECT user FROM dbl", isSelect=True, fetchAll=True)
        voters = []
        for vote in votes:
            voters.append(vote[0])
        print(voters)
        if str(ctx.message.author.id) in voters:
            await ctx.send("yay")
        else:
            await ctx.send("Nay")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(200, 20, commands.BucketType.user)
    async def pgif(self, ctx):
        """Posts a Random PrOn GIF"""
        votes = await self.execute("SELECT user FROM dbl", isSelect=True, fetchAll=True)
        voters = []
        for vote in votes:
            voters.append(vote[0])
        if str(ctx.message.author.id) in voters:
            if not ctx.message.channel.is_nsfw():
                await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
                return
            self.counter['pgif'] += 1
            async with aiohttp.ClientSession() as cs:
                async with cs.get("http://37.59.36.62:10000/pgif") as r:
                    res = await r.json()
            x = "http://37.59.36.62/pgif/" + res['msg']
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=x)

            await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="WOAH",
                                  description="Have you voted yet <:smirkGuns:417969421252952085>\n"
                                              "https://discordbots.org/bot/310039170792030211/vote")
            if not ctx.message.channel.is_nsfw():
                embed.set_footer(text="Use in a NSFW Channel BTW...")
            await ctx.send(embed=embed)

    @commands.command(name="4k")
    @commands.guild_only()
    async def _fourk(self, ctx):
        """Posts a random 4K Image OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter["4k"] += 1
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://37.59.36.62:10000/4kdata") as r:
                res = await r.json()
        data = res['msg']
        embed = discord.Embed(color=0xDEADBF)
        url = "http://37.59.36.62/4k/" + data
        embed.set_image(url=url)
        await ctx.send(embed=embed.set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    async def phsearch(self, ctx, terms: str):
        """Search from PronHub"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        try:
            self.counter["phsearch"] += 1
            searchurl = "https://www.pornhub.com/video/search?search={}".format(terms.replace(" ", "+"))
            url = requests.get(searchurl).text
            soup = bs(url)
            phtitle = soup.find("a", {"class": "img"})['title']
            phurl = soup.find("a", {"class": "img"})['href']
            href = "https://www.pornhub.com{}".format(phurl)
            em = discord.Embed(title=phtitle,
                               color=0xDEADBF,
                               description=href)
            await ctx.send(embed=em)
        except Exception as e:
            await ctx.send(embed=discord.Embed(title="Error",
                                               color=0xDEADBF,
                                               description="**`{}`**".format(e)).set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    async def yandere(self, ctx, *tags: str):
        """Search Yande.re OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        if tags == ():
            await ctx.send(":warning: Tags are missing.")
        else:
            try:
                self.counter["yandere"] += 1
                tags = ("+").join(tags)
                query = ("https://yande.re/post.json?limit=42&tags=" + tags)
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(query) as r:
                        res = await r.json()
                if res != []:
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=random.choice(res)['jpeg_url'])
                    await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))
                else:
                    e = discord.Embed(color=0xDEADBF, title="⚠ Error",
                                      description="Yande.re has no images for requested tags.")
                    await ctx.send(embed=e)
            except Exception as e:
                await ctx.send(":x: `{}`".format(e))

    @commands.command()
    @commands.guild_only()
    async def boobs(self, ctx):
        """Get Random Boobs OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        try:
            self.counter["boobs"] += 1
            rdm = random.randint(0, 11545)
            search = ("http://api.oboobs.ru/boobs/{}".format(rdm))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(search) as r:
                    res = await r.json()
                    boob = random.choice(res)
                    boob = "http://media.oboobs.ru/{}".format(boob["preview"])
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=boob)
                    await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))
        except Exception as e:
            await ctx.send("**`{}`**".format(e))

    @commands.command()
    @commands.guild_only()
    async def girl(self, ctx):
        """Get a girl OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['girl'] += 1
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/bodyperfection/hot/{random.randint(1, 5)}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res =  await r.json()
        data = res['data']
        x = random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    async def bigboobs(self, ctx):
        """Big Boobs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['bigboobs'] += 1
        sub = random.choice(["bigboobs", "BigBoobsGW"])
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/{sub}/hot/{random.randint(1, 5)}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
        x = random.choice(res['data'])
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    async def ass(self, ctx):
        """Get Random Ass OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['ass'] += 1
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/asstastic/hot/{random.randint(1, 5)}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
        x = random.choice(res['data'])
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command(aliases=["cum"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cumsluts(self, ctx):
        """CumSluts"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['cum'] += 1
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/cumsluts/hot/{random.randint(1, 5)}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
        x = random.choice(res['data'])
        embed = discord.Embed(color=0xDEADBF,
                              title=f"**{x['title']}**")
        embed.set_image(url=x['link'])

        await ctx.send(embed=embed.set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def thighs(self, ctx):
        """Thighs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        sub = random.choice(["thighhighs", "stockings"])
        self.counter['thighs'] += 1
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/{sub}/hot/{random.randint(1, 5)}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
        x = random.choice(res['data'])
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    async def gonewild(self, ctx):
        """r/GoneWild"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['gonewild'] += 1
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/gonewild/hot/{random.randint(1, 5)}'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
        x = random.choice(res['data'])
        em = discord.Embed(title=f"**{x['title']}**", color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    async def doujin(self, ctx):
        """Get a Random Doujin"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        else:
            url = "http://nhentai.net/random/"
            await ctx.send(embed=discord.Embed(color=0xDEADBF, description=f"{url}").set_footer(text=f"Used by {ctx.message.author.name}"))

    @commands.command()
    @commands.guild_only()
    async def hentai(self, ctx, type:str = None):
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['hentai'] += 1
        # amount = await self.execute(f'SELECT 1 FROM dbl WHERE user = {ctx.message.author.id} AND type = \"upvote\"', isSelect=True)
        # if amount:
        votes = await self.execute("SELECT user FROM dbl", isSelect=True, fetchAll=True)
        voters = []
        for vote in votes:
            voters.append(vote[0])
        if str(ctx.message.author.id) in voters:
            types = ['cum', 'les', 'Random_hentai_gif', 'bj', 'nsfw_neko_gif', 'anal', 'pussy', 'classic', 'kuni', 'boobs', 'Random_hentai_gif']
            if type is None:
                x = random.choice(types)
            elif not type in types:
                return await ctx.send(f"Invalid type. List of types: `{types}`")
            else:
                x = type
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://nekos.life/api/v2/img/{x}") as r:
                    res = await r.json()
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=res['url'])
                    await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="oof",
                                  description="Have you voted yet <:smirkGuns:417969421252952085>\n"
                                              "https://discordbots.org/bot/310039170792030211/vote")
            await ctx.send(embed=embed)

    @commands.command(name="rule34", aliases=["r34"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def rule34(self, ctx, tag:str):
        """Search rule34"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}") as r:
                    data = json.loads(await r.text())
            non_loli = list(filter(lambda x: 'loli' not in x['tags'] and 'shota' not in x['tags'], data))
            if len(non_loli) == 0:
                em = discord.Embed(color=0xff6f3f, title="Warning", description="Loli/Shota in search.")
                return await ctx.send(embed=em)
            response = non_loli[random.randint(0, len(non_loli) - 1)]
            img = f"https://img.rule34.xxx/images/{response['directory']}/{response['image']}"
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=img)
            await ctx.send(embed=em.set_footer(text=f"Used by {ctx.message.author.name}"))
        except json.JSONDecodeError:
            await ctx.send(":x: No image found. Sorry :/")

    @commands.command()
    @commands.guild_only()
    async def nsfw(self, ctx):
        """NSFW Stats"""
        embed = discord.Embed(color=0xDEADBF,
                              title="NSFW Stats")
        embed.add_field(name="PGIF", value=self.counter['pgif'])
        embed.add_field(name="4k", value=self.counter['4k'])
        embed.add_field(name="Yande.re", value=self.counter['yandere'])
        embed.add_field(name="Ass", value=self.counter['ass'])
        embed.add_field(name="Boobs", value=self.counter['boobs'])
        embed.add_field(name="Cumsluts", value=self.counter['cum'])
        embed.add_field(name="Thighs", value=self.counter['thighs'])
        embed.add_field(name="GoneWild", value=self.counter['gonewild'])
        embed.add_field(name="Girl", value=self.counter['girl'])
        embed.add_field(name="Big Boobs", value=self.counter['bigboobs'])
        embed.add_field(name="Hentai", value=self.counter['hentai'])

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(NSFW(bot))
