from discord.ext import commands
import discord, random, aiohttp
from .utils import checks, chat_formatting, hastebin
import config
import json
import gettext

class NSFW:
    """NSFW Commands OwO"""

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("nsfw", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

    async def log_error(self, error:str):
        webhook_url = f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}"
        async with aiohttp.ClientSession() as cs:
            webhook = discord.Webhook.from_url(webhook_url, adapter=discord.AsyncWebhookAdapter(cs))

            em = discord.Embed(color=0xff6f3f)
            em.title = "Error"
            em.description = chat_formatting.box(error, "python")
            em.set_footer(text="Instance %s" % self.bot.instance)

            await webhook.send(embed=em)

    async def nekobot(self, imgtype: str):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekobot.xyz/api/image?type=%s" % imgtype) as res:
                res = await res.json()
        return res.get("message")

    async def boobbot(self, imgtype:str):
        auth = {"key": config.boobbot["key"]}
        url = "https://nekobot.xyz/placeholder.png"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(config.boobbot["base"] + imgtype, headers=auth) as res:
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
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot("pgif"))

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(10, 10, commands.BucketType.user)
    async def yaoi(self, ctx):
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            return await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("yaoi"))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def anal(self, ctx):
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        embed = discord.Embed(color=0xDEADBF)
        embed.set_image(url=await self.nekobot("anal"))
        await ctx.send(embed=embed)

    @commands.command(name="4k")
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def _fourk(self, ctx):
        """Posts a random 4K Image OwO"""
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        embed = discord.Embed(color=0xDEADBF)
        embed.set_image(url=await self.nekobot("4k"))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def yandere(self, ctx, tag: str):
        """Search Yande.re OwO"""
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        else:
            query = ("https://yande.re/post.json?limit=100&tags=" + tag)
            async with aiohttp.ClientSession() as cs:
                async with cs.get(query) as res:
                    res = await res.json()
            if res != []:
                img = random.choice(res)
                if "loli" in img["tags"] or "shota" in img["tags"]:
                    return await ctx.send(_("Loli or shota was found in this post."))
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
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            return await ctx.send(_("This is not an NSFW channel..."), delete_after=5)
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("boobs"))
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
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as res:
                res =  await res.json()
        if res["status"] == 429:
            _ = await self._get_text(ctx)
            return await ctx.send(_("**Ratelimited, try again later.**"))
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
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as res:
                res = await res.json()
        if res["status"] == 429:
            _ = await self._get_text(ctx)
            return await ctx.send(_("**Ratelimited, try again later.**"))
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
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot("ass"))

        await ctx.send(embed=em)

    @commands.command(aliases=["cum"])
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def cumsluts(self, ctx):
        """CumSluts"""
        if not ctx.message.channel.is_nsfw():
            _ = await self._get_text(ctx)
            return await ctx.send(_("This is not an NSFW channel..."), delete_after=5)
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("cumsluts"))
        await ctx.send(embed=em)

    @commands.command(aliases=["thigh"])
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def thighs(self, ctx):
        """Thighs"""
        if not ctx.message.channel.is_nsfw():
            _ = await self._get_text(ctx)
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        em = discord.Embed(color=0xDEADBF)
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekobot.xyz/api/v2/image/thighs") as res:
                res = await res.json()
        em.set_image(url=res["message"])
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def pussy(self, ctx):
        """Pussy owo"""
        if not ctx.message.channel.is_nsfw():
            _ = await self._get_text(ctx)
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot("pussy"))

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def gonewild(self, ctx):
        """r/GoneWild"""
        if not ctx.message.channel.is_nsfw():
            _ = await self._get_text(ctx)
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot("gonewild"))

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(3, 7, commands.BucketType.user)
    async def doujin(self, ctx):
        """Get a Random Doujin"""
        if not ctx.message.channel.is_nsfw():
            _ = await self._get_text(ctx)
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        else:
            async with aiohttp.ClientSession() as cs:
                async with cs.get("http://nhentai.net/random/") as res:
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
            _ = await self._get_text(ctx)
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>"))
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot("lewdkitsune"))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def hentai(self, ctx):
        """Lood 2d girls"""
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            await ctx.send(_("This is not a NSFW Channel <:deadStare:417437129501835279>\nhttps://nekobot.xyz/hentai.png"))
            return
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.nekobot("hentai"))
        await ctx.send(embed=em)

    @commands.command(name="rule34", aliases=["r34"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.guild_only()
    async def rule34(self, ctx, tag:str):
        """Search rule34"""
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            return await ctx.send(_("This is not an NSFW channel..."), delete_after=5)
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}") as res:
                    data = json.loads(await res.text())
            non_loli = list(filter(lambda x: 'loli' not in x['tags'] and 'shota' not in x['tags'], data))
            if len(non_loli) == 0:
                em = discord.Embed(color=0xff6f3f, title="Warning", description=_("Loli/Shota in search."))
                return await ctx.send(embed=em)
            response = non_loli[random.randint(0, len(non_loli) - 1)]
            img = f"https://img.rule34.xxx/images/{response['directory']}/{response['image']}"
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=img)
            await ctx.send(embed=em)
        except json.JSONDecodeError:
            await ctx.send(_(":x: No image found. Sorry :/"))

    @commands.command()
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.guild_only()
    async def e621(self, ctx, tag:str):
        """Search e621"""
        _ = await self._get_text(ctx)
        if not ctx.message.channel.is_nsfw():
            return await ctx.send(_("This is not an NSFW channel..."), delete_after=5)
        try:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
            async with ctx.typing():
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://e621.net/post/index.json?limit=15&tags={tag}",
                                      headers={"User-Agent": ua}) as res:
                        res = await res.json()
                data = random.choice(res)
                if data == []:
                    return await ctx.send(_("**No images found**"))
                if "loli" in data["tags"] or "shota" in data["tags"]:
                    return await ctx.send(_("**Loli/Shota found in image.**"))
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=data["file_url"])
                await ctx.send(embed=em)
        except:
            await ctx.send(_("**Could not find anything.**"))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def futa(self, ctx):
        """Grils with peepee's"""
        if not ctx.message.channel.is_nsfw():
            _ = await self._get_text(ctx)
            return await ctx.send(_("This is not an NSFW channel..."), delete_after=5)
        em = discord.Embed(color=0xDEADBF)
        em.set_image(url=await self.boobbot("futa"))
        await ctx.send(embed=em)

    @commands.command(aliases=["collar"])
    @commands.guild_only()
    @commands.cooldown(25, 10, commands.BucketType.user)
    async def collared(self, ctx):
        if not ctx.message.channel.is_nsfw():
            _ = await self._get_text(ctx)
            return await ctx.send(_("This is not an NSFW channel..."), delete_after=5)
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
        _ = await self._get_text(ctx)
        try:
            if channel.is_nsfw():
                await channel.edit(nsfw=False)
                await ctx.send(_("I have removed NSFW permissions from %s") % channel.name)
            else:
                await channel.edit(nsfw=True)
                await ctx.send(_("I have have made %s an NSFW channel for you <3") % channel.name)
        except:
            try:
                await ctx.send(_("I can't make that channel NSFW or don't have permissions to ;c"))
            except:
                pass

def setup(bot):
    bot.add_cog(NSFW(bot))
