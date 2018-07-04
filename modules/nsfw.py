from discord.ext import commands
import discord, random, aiohttp, requests
from bs4 import BeautifulSoup as bs
from .utils import checks, chat_formatting, hastebin
import config
import json
import nekobot

class NSFW:
    """NSFW Commands OwO"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.nekobot = nekobot.Client(loop=self.bot.loop)

    async def execute(self, query: str, isSelect: bool = False, fetchAll: bool = False, commit: bool = False):
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(query)
                if isSelect:
                    if fetchAll:
                        values = await db.fetchall()
                    else:
                        values = await db.fetchone()
                if commit:
                    await conn.commit()
            if isSelect:
                return values

    async def log_error(self, error:str):
        webhook_url = f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}"
        webhook = discord.Webhook.from_url(webhook_url, adapter=discord.AsyncWebhookAdapter(self.session))

        em = discord.Embed(color=0xff6f3f)
        em.title = "Error"
        em.description = chat_formatting.box(error, "python")
        em.set_footer(text="Instance %s" % self.bot.instance)

        await webhook.send(embed=em)

    async def boobbot(self, imgtype:str):
        url = config.boobbot["base"] + imgtype
        auth = {"key": config.boobbot["key"]}
        data = await self.session.get(url, headers=auth)

        try:
            x = await data.json()
        except aiohttp.ContentTypeError:
            content = await data.text()
            status = data.status
            content = await hastebin.post(str(content))
            await self.log_error(f"Content Type Error:\n({status}) {content}")
            return "https://nekobot.xyz/placeholder.png"
        return x.get("url")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(200, 20, commands.BucketType.user)
    async def pgif(self, ctx):
        """Posts a Random PrOn GIF"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        if await self.execute(f"SELECT 1 FROM dbl WHERE user = %s" % ctx.author.id, isSelect=True):
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=await self.nekobot.image("pgif"))

            await ctx.send(embed=em)
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="WOAH",
                                  description="Have you voted yet <:smirkGuns:417969421252952085>\n"
                                              "https://discordbots.org/bot/310039170792030211/vote")
            if not ctx.message.channel.is_nsfw():
                embed.set_footer(text="Use in a NSFW Channel BTW...")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def anal(self, ctx):
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        embed = discord.Embed(color=0xDEADBF)
        embed.set_image(url=await self.nekobot.image("anal"))
        await ctx.send(embed=embed)

    @commands.command(aliases=["DVA", "d.va"])
    @commands.guild_only()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def dva(self, ctx):
        await ctx.trigger_typing()
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://api.computerfreaker.cf/v1/dva") as r:
                res = await r.json()
        data = res['url']
        embed = discord.Embed(color=0xDEADBF)
        embed.set_image(url=data)
        await ctx.send(embed=embed)

    @commands.command(name="4k")
    @commands.guild_only()
    async def _fourk(self, ctx):
        """Posts a random 4K Image OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        embed = discord.Embed(color=0xDEADBF)
        embed.set_image(url=await self.nekobot.image("4k"))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def phsearch(self, ctx, terms: str):
        """Search from PronHub"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        try:
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
    async def yandere(self, ctx, tag: str):
        """Search Yande.re OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        else:
            try:
                query = ("https://yande.re/post.json?limit=100&tags=" + tag)
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(query) as r:
                        res = await r.json()
                if res != []:
                    img = random.choice(res)
                    if "loli" in img["tags"] or "shota" in img["tags"]:
                        return await ctx.send("Loli or shota was found in this post.")
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=img['jpeg_url'])
                    await ctx.send(embed=em)
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
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("boobs"))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def girl(self, ctx):
        """Get a girl OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
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

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def bigboobs(self, ctx):
        """Big Boobs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
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

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def ass(self, ctx):
        """Get Random Ass OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot.image("ass"))

        await ctx.send(embed=em)

    @commands.command(aliases=["cum"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cumsluts(self, ctx):
        """CumSluts"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("cumsluts"))
        await ctx.send(embed=em)

    @commands.command(aliases=["thigh"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def thighs(self, ctx):
        """Thighs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot.image("thigh"))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pussy(self, ctx):
        """Pussy owo"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot.image("pussy"))

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def gonewild(self, ctx):
        """r/GoneWild"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot.image("gonewild"))

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def doujin(self, ctx):
        """Get a Random Doujin"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        else:
            url = "http://nhentai.net/random/"
            res = await self.session.get(url)
            url = res.url
            await ctx.send(embed=discord.Embed(color=0xDEADBF,
                                               title="Random Doujin",
                                               description=str(url)))

    @commands.command()
    @commands.guild_only()
    async def lewdkitsune(self, ctx):
        """Lewd Kitsunes"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot.image("lewdkitsune"))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def hentai(self, ctx):
        """Lood 2d girls"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>\nhttps://nekobot.xyz/hentai.png")
            return
        if await self.execute("SELECT 1 FROM dbl WHERE user = %s" % ctx.author.id, isSelect=True):
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=await self.nekobot.image("hentai"))
            await ctx.send(embed=em)
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
            await ctx.send(embed=em)
        except json.JSONDecodeError:
            await ctx.send(":x: No image found. Sorry :/")

    @commands.command(name="rule34magik", aliases=["r34magik", "r34m"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def rule34m(self, ctx, tag:str):
        """Magikify Rule34 Searches"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        try:
            async with ctx.typing():
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}") as r:
                        data = json.loads(await r.text())
                non_loli = list(filter(lambda x: 'loli' not in x['tags'] and 'shota' not in x['tags'], data))
                if len(non_loli) == 0:
                    em = discord.Embed(color=0xff6f3f, title="Warning", description="Loli/Shota in search.")
                    return await ctx.send(embed=em)
                response = non_loli[random.randint(0, len(non_loli) - 1)]
                img = f"https://img.rule34.xxx/images/{response['directory']}/{response['image']}"
                async with aiohttp.ClientSession() as cs:
                    async with cs.get("https://nekobot.xyz/api/imagegen?type=magik&image="+img) as r:
                        res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                if not res["success"]:
                    return await ctx.send(f"**Failed to magikify a rule34 search**, `{res['message']}`")
                em.set_image(url=res["message"])
                await ctx.send(embed=em)
        except json.JSONDecodeError:
            await ctx.send(":x: No image found. Sorry :/")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def e621(self, ctx, tag:str):
        """Search e621"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        try:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
            async with ctx.typing():
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://e621.net/post/index.json?limit=15&tags={tag}",
                                      headers={"User-Agent": ua}) as r:
                        res = await r.json()
                data = random.choice(res)
                if data == []:
                    return await ctx.send("**No images found**")
                if data["has_children"]:
                    return await ctx.send("**Children found in image.**")
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=data["file_url"])
                await ctx.send(embed=em)
        except:
            await ctx.send("**Failed to connect to e621**")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def futa(self, ctx):
        """Grils with peepee's"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("futa"))
        await ctx.send(embed=em)

    @commands.command(aliases=["collar"])
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def collared(self, ctx):
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("collared"))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @checks.is_admin()
    async def nsfw(self, ctx, channel:discord.TextChannel = None):
        """Make a channel NSFW."""
        if channel is None:
            channel = ctx.message.channel

        try:
            if channel.is_nsfw():
                await channel.edit(nsfw=False)
                await ctx.send(f"I have removed NSFW permissions from {channel.name}")
            else:
                await channel.edit(nsfw=True)
                await ctx.send(f"I have have made {channel.name} an NSFW channel for you <3")
        except:
            try:
                await ctx.send("I can't make that channel NSFW or don't have permissions to ;c")
            except:
                pass

def setup(bot):
    bot.add_cog(NSFW(bot))
