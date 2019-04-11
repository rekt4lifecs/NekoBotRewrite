from discord.ext import commands
import discord, random, aiohttp
from .utils import checks, chat_formatting, hastebin, helpers
import config
import json
from bs4 import BeautifulSoup
import re

url_rx = re.compile("https?:\/\/(?:www\.)?.+")
creator_rx = re.compile(r"Creator: <\/strong>([\w\d\s\-_.*()\[\]]*)<br\/>")
material_rx = re.compile(r"Material: <\/strong>([\w\d\s\-_.*()\[\]]*)<br\/>")
author_rx = re.compile(r"Author: <\/strong><[\w\s\d=\"\-_\.\/\?:]*>([\w\d\s\-_.*()\[\]]*)<\/a>")
member_rx = re.compile(r"Member: <\/strong><[\w\s\d=\"\-_\.\/\?:]*>([\w\d\s\-_.*()\[\]]*)<\/a>")
deviant_art_rx = re.compile(r"[\w]+\.deviantart\.com")
deviant_source_rx = re.compile(r"deviantart\.com\/view\/")
pixiv_art_rx = re.compile(r"pixiv\.net\/member\.")
pixiv_source_rx = re.compile(r"pixiv\.net\/member_illust")
gelbooru_rx = re.compile(r"gelbooru\.com\/index\.php\?page")
danbooru_rx = re.compile(r"danbooru\.donmai\.us\/post\/")
sankaku_rx = re.compile(r"chan\.sankakucomplex\.com\/post")

class NSFW(commands.Cog):
    """NSFW Commands OwO"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.session.close()
        del self.session

    async def log_error(self, error:str):
        webhook_url = f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}"
        webhook = discord.Webhook.from_url(webhook_url, adapter=discord.AsyncWebhookAdapter(self.session))

        em = discord.Embed(color=0xff6f3f)
        em.title = "Error"
        em.description = chat_formatting.box(error, "python")
        em.set_footer(text="Instance %s" % self.bot.instance)

        await webhook.send(embed=em)

    async def nekobot(self, imgtype: str):
        async with self.session.get("https://nekobot.xyz/api/image?type=%s" % imgtype) as res:
            res = await res.json()
        return res.get("message")

    async def boobbot(self, imgtype:str):
        auth = {"key": config.boobbot["key"]}
        url = "https://nekobot.xyz/placeholder.png"
        async with self.session.get(config.boobbot["base"] + imgtype, headers=auth) as res:
            try:
                x = await res.json()
                url = x.get("url")
            except:
                content = await res.text()
                status = res.status
                content = await hastebin.post(str(content))
                await self.log_error(f"Content Type Error:\n({status}) {content}")
        return url

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def pgif(self, ctx):
        """Posts a Random PrOn GIF"""

        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        image = await self.nekobot("pgif")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(10, 10, commands.BucketType.user)
    async def yaoi(self, ctx):

        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")

        image = await self.boobbot("yaoi")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def anal(self, ctx):

        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return

        image = await self.nekobot("anal")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command(name="4k")
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def _fourk(self, ctx):
        """Posts a random 4K Image OwO"""

        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        image = await self.nekobot("4k")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def yandere(self, ctx, tag: str):
        """Search Yande.re OwO"""

        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        else:
            query = ("https://yande.re/post.json?limit=100&tags=" + tag)
            async with self.session.get(query) as res:
                res = await res.json()
        if res != []:
            img = random.choice(res)
            if "loli" in img["tags"] or "shota" in img["tags"]:
                return await ctx.send("Loli or shota was found in this post.")
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=img['jpeg_url'])
            await ctx.send(embed=em)
        else:
            await ctx.send("No tags found.")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def boobs(self, ctx):
        """Get Random Boobs OwO"""

        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)

        image = await self.boobbot("boobs")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def girl(self, ctx):
        """Get a girl OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/bodyperfection/hot/{random.randint(1, 5)}'
        async with self.session.get(url, headers=headers) as res:
            res =  await res.json()
        if res["status"] == 429:
            return await ctx.send("**Ratelimited, try again later.**")
        data = res['data']
        x = random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def bigboobs(self, ctx):
        """Big Boobs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        sub = random.choice(["bigboobs", "BigBoobsGW"])
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        url = f'https://api.imgur.com/3/gallery/r/{sub}/hot/{random.randint(1, 5)}'
        async with self.session.get(url, headers=headers) as res:
            res = await res.json()
        if res["status"] == 429:
            return await ctx.send("**Ratelimited, try again later.**")
        x = random.choice(res['data'])
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def ass(self, ctx):
        """Get Random Ass OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return

        image = await self.nekobot("ass")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command(aliases=["cum"])
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def cumsluts(self, ctx):
        """CumSluts"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        image = await self.boobbot("cumsluts")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)
        await ctx.send(embed=em)

    @commands.command(aliases=["thigh"])
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def thighs(self, ctx):
        """Thighs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        async with self.session.get("https://nekobot.xyz/api/v2/image/thighs") as res:
            res = await res.json()
        image = res["message"]
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def pussy(self, ctx):
        """Pussy owo"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return

        image = await self.nekobot("pussy")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def gonewild(self, ctx):
        """r/GoneWild"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return

        image = await self.nekobot("gonewild")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(3, 7, commands.BucketType.user)
    async def doujin(self, ctx):
        """Get a Random Doujin"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        else:
            async with self.session.get("http://nhentai.net/random/") as res:
                res = res.url
            await ctx.send(embed=discord.Embed(color=0xDEADBF,
                                               title="Random Doujin",
                                               description=str(res)))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def lewdkitsune(self, ctx):
        """Lewd Kitsunes"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        image = await self.nekobot("lewdkitsune")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def hentai(self, ctx):
        """Lood 2d girls"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>\nhttps://nekobot.xyz/hentai.png")
            return
        image = await self.nekobot("hentai")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)
        await ctx.send(embed=em)

    @commands.command(name="rule34", aliases=["r34"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.guild_only()
    async def rule34(self, ctx, tag:str):
        """Search rule34"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        try:
            async with self.session.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}") as res:
                data = json.loads(await res.text())
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

    @commands.command()
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.guild_only()
    async def e621(self, ctx, tag:str):
        """Search e621"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        try:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
            async with ctx.typing():
                async with self.session.get(f"https://e621.net/post/index.json?limit=15&tags={tag}",
                                  headers={"User-Agent": ua}) as res:
                    res = await res.json()
                data = random.choice(res)
                if data == []:
                    return await ctx.send("**No images found**")
                if "loli" in data["tags"] or "shota" in data["tags"]:
                    return await ctx.send("**Loli/Shota found in image.**")
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=data["file_url"])
                await ctx.send(embed=em)
        except:
            await ctx.send("**Could not find anything.**")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def futa(self, ctx):
        """Grils with peepee's"""
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        image = await self.boobbot("futa")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)
        await ctx.send(embed=em)

    @commands.command(aliases=["collar"])
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def collared(self, ctx):
        if not ctx.message.channel.is_nsfw():
            return await ctx.send("This is not an NSFW channel...", delete_after=5)
        image = await self.boobbot("collared")
        em = discord.Embed(color=await helpers.get_dominant_color(self.bot, image))
        em.set_image(url=image)
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
                await ctx.send("I have removed NSFW permissions from %s" % channel.name)
            else:
                await channel.edit(nsfw=True)
                await ctx.send("I have have made %s an NSFW channel for you owo" % channel.name)
        except:
            try:
                await ctx.send("I can't make that channel NSFW or don't have permissions to ;c")
            except:
                pass

    @commands.command(aliases=["sauce", "saucenao"])
    @commands.guild_only()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def source(self, ctx, image_url=None):
        """Get images sources from SourceNAO"""
        if not ctx.channel.is_nsfw():
            return await ctx.send("Please use this in an NSFW channel.", delete_after=5)

        if image_url is None and len(ctx.message.attachments) == 0:
            await ctx.send("Send me an image to get the source of")
            try:
                msg = await self.bot.wait_for("message", timeout=30.0, check=lambda x: x.author.id == ctx.author.id and x.channel.id == ctx.channel.id)
                if len(msg.attachments) >= 1:
                    image_url = msg.attachments[0].url
                else:
                    image_url = msg.content
            except:
                return await ctx.send("Timed out")
        if len(ctx.message.attachments) >= 1 and image_url is None:
            image_url = ctx.message.attachments[0].url
        if not url_rx.match(image_url):
            return await ctx.send("That's not a valid image.")

        await ctx.trigger_typing()
        async with self.session.get("http://saucenao.com/search.php?db=999&url={}".format(image_url)) as res:
            data = await res.read()

        if b"Problem with remote server..." in data:
            return await ctx.send("Could not find the source for that image.")

        em = discord.Embed(title="Results", color=0xDEADBF)
        description = ""
        soup = BeautifulSoup(data, "html.parser")

        creator = creator_rx.search(str(soup))
        if creator is not None:
            description += "Creator: **{}**\n".format(creator.group(1))
        material = material_rx.search(str(soup))
        if material is not None:
            description += "Material: **{}**\n".format(material.group(1))
        author = author_rx.search(str(soup))
        if author is not None:
            description += "Author: **{}**\n".format(author.group(1))
        member = member_rx.search(str(soup))
        if member is not None:
            description += "Member: **{}**\n".format(member.group(1))
        links = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if deviant_art_rx.search(href) and not [1 for x, y in links if x == "DeviantArt Artist"]:
                links.append(["DeviantArt Artist", href])
            if deviant_source_rx.search(href) and not [1 for x, y in links if x == "DeviantArt Source"]:
                links.append(["DeviantArt Source", href])
            if pixiv_art_rx.search(href) and not [1 for x, y in links if x == "Pixiv Artist"]:
                links.append(["Pixiv Artist", href])
            if pixiv_source_rx.search(href) and not [1 for x, y in links if x == "Pixiv Source"]:
                links.append(["Pixiv Source", href])
            if gelbooru_rx.search(href) and not [1 for x, y in links if x == "Gelbooru"]:
                links.append(["Gelbooru", href])
            if danbooru_rx.search(href) and not [1 for x, y in links if x == "Danbooru"]:
                links.append(["Danbooru", href])
            if sankaku_rx.search(href) and not [1 for x, y in links if x == "Sankaku"]:
                links.append(["Sankaku", href])

        description += ", ".join(["[{}]({})".format(x, y) for x, y in links])

        em.description = description
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(NSFW(bot))
