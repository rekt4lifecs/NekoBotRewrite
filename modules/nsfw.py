from discord.ext import commands
import discord, random, aiohttp, config, requests
from bs4 import BeautifulSoup as bs
from collections import Counter

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

class NSFW:
    """NSFW Commands OwO"""

    def __init__(self, bot):
        self.bot = bot
        self.fourk = config.fourkdata
        self.pgifdata = config.pgifdata
        self.counter = Counter()

    @commands.command()
    @commands.guild_only()
    async def pgif(self, ctx):
        """Posts a Random PrOn GIF"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter["pgif"] += 1
        data = random.choice(self.pgifdata)
        embed = discord.Embed(color=0xDEADBF)
        url = "http://37.59.36.62/pgif/" + data
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(name="4k")
    @commands.guild_only()
    async def _fourk(self, ctx):
        """Posts a random 4K Image OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter["4k"] += 1
        data = random.choice(self.fourk)
        embed = discord.Embed(color=0xDEADBF)
        url = "http://37.59.36.62/4k/" + data
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def phsearch(self, ctx, terms : str):
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
                                               description="**`{}`**".format(e)))

    @commands.command()
    @commands.guild_only()
    async def lewdneko(self, ctx):
        """Posts a Lewd Neko OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter["lewdneko"] += 1
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://nekos.life/api/lewd/neko') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['neko'])
                await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def yandere(self, ctx, *tags : str):
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
                    await ctx.send(embed=em)
                else:
                    await ctx.send(":warning: Yande.re has no images for requested tags.")
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
                    await ctx.send(embed=em)
        except Exception as e:
            await ctx.send("**`{}`**".format(e))

    @commands.command()
    @commands.guild_only()
    async def ass(self, ctx):
        """Get Random Ass OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        try:
            self.counter["ass"] += 1
            rdm = random.randint(0, 5538)
            search = ("http://api.obutts.ru/butts/{}".format(rdm))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(search) as r:
                    res = await r.json()
                    butt = random.choice(res)
                    butt = "http://media.obutts.ru/{}".format(butt["preview"])
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=butt)
                    await ctx.send(embed=em)
        except Exception as e:
            await ctx.send("**`{}`**".format(e))

    @commands.command(aliases=["cum"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cumsluts(self, ctx):
        """CumSluts"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['cum'] += 1
        data = config.imgur._get_imgur(self, "cumsluts")['data']
        x = random.choice(data)
        embed = discord.Embed(color=0xDEADBF,
                              title=f"**{x['title']}**")
        embed.set_image(url=x['link'])

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lingerie(self, ctx):
        """Lingerie"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['lingerie'] += 1
        data = config.imgur._get_imgur(self, "lingerie", page=random.randint(1, 5))['data']
        x =  random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gonewild(self, ctx):
        """r/GoneWild"""
        url = "https://discordbots.org/api/bots/310039170792030211/votes"
        async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
            async with cs.get(url) as r:
                res = await r.json()
        for x in res:
            if str(x['id']) == str(ctx.message.author.id):
                if not ctx.message.channel.is_nsfw():
                    await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
                    return
                self.counter['gonewild'] += 1
                data = config.imgur._get_imgur(self, "gonewild", page=random.randint(1, 5))['data']
                x = random.choice(data)
                em = discord.Embed(title=f"**{x['title']}**",
                                   color=0xDEADBF)
                em.set_image(url=x['link'])

                await ctx.send(embed=em)
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="WOAH",
                                  description="Have you voted yet >.>\n\n"
                                              "https://discordbots.org/bot/310039170792030211/vote")
            if ctx.message.channel.is_nsfw():
                embed.set_footer(text="Use in a NSFW Channel BTW...")
            await ctx.send(embed=embed)



    @commands.command()
    async def nsfw(self, ctx):
        """NSFW Stats"""
        embed = discord.Embed(color=0xDEADBF,
                              title="NSFW Stats")
        embed.add_field(name="PGIF", value=self.counter['pgif'])
        embed.add_field(name="4k", value=self.counter['4k'])
        embed.add_field(name="Lewd Neko", value=self.counter['lewdneko'])
        embed.add_field(name="Yande.re", value=self.counter['yandere'])
        embed.add_field(name="Ass", value=self.counter['ass'])
        embed.add_field(name="Boobs", value=self.counter['boobs'])
        embed.add_field(name="Cumsluts", value=self.counter['cum'])
        embed.add_field(name="Lingerie", value=self.counter['lingerie'])
        embed.add_field(name="GoneWild", value=self.counter['gonewild'])

        await ctx.send(embed=embed)

        ### TKINTER ERROR #TODO
        # objects = ('PGIF', '4k', 'search', 'lewd\nneko', 'Yande.re', 'Ass', 'Boobs', "Cum", "Lingerie")
        # y_pos = np.arange(len(objects))
        # performance = [self.counter["pgif"], self.counter["4k"], self.counter["phsearch"], self.counter["lewdneko"],
        #                self.counter["yandere"], self.counter["ass"], self.counter["boobs"], self.counter['cum'], self.counter['lingerie']]
        # plt.bar(y_pos, performance, align='center', alpha=0.5)
        # plt.xticks(y_pos, objects)
        # plt.ylabel('Usage')
        # plt.title('NSFW Command Usage')
        # plt.savefig("data/nsfw.png")
        # file = discord.File("data/nsfw.png")
        # await ctx.send(file=file)


def setup(bot):
    bot.add_cog(NSFW(bot))
