from discord.ext import commands
import discord
from .utils.weeb import Weeb
import config
import aiohttp
from random import choice as randchoice

class TestWeeb:

    def __init__(self, bot):
        self.bot = bot
        self.weeb = Weeb(config.weeb, bot)

    async def __local_check(self, ctx):
        return True if ctx.guild else False

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def awoo(self, ctx):
        """Awooo!"""
        color, url = await self.weeb.awoo()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bang(self, ctx, user: discord.Member):
        if user == ctx.author:
            title = "Banged self ;w;"
        else:
            title = "%s banged %s >:)" % (ctx.author.name, user.name,)

        color, url = await self.weeb.bang()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blush(self, ctx):
        """>///<"""
        color, url = await self.weeb.blush()
        em = discord.Embed(color=color, title="%s blushes >///<" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def confused(self, ctx):
        """???"""
        color, url = await self.weeb.clagwimoth()
        em = discord.Embed(color=color, title="%s is confused ;w;" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dance(self, ctx):
        """Dance uwu"""
        color, url = await self.weeb.dance()
        em = discord.Embed(color=color, title="*%s dances*" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def insult(self, ctx, user: discord.Member):
        """Insult someone owo"""
        if user == ctx.author:
            title = "%s insulted themself ;w;" % ctx.author.name
        else:
            title = "%s insulted %s >:)" % (ctx.author.name, user.name,)

        color, url = await self.weeb.insult()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cry(self, ctx):
        """*cries*"""
        color, url = await self.weeb.cry()
        em = discord.Embed(color=color, title="*%s cries*" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def jojo(self, ctx):
        color, url = await self.weeb.jojo()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def megumin(self, ctx):
        color, url = await self.weeb.megumin()
        em = discord.Embed(color=color, title="Explosion!").set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pout(self, ctx):
        color, url = await self.weeb.pout()
        em = discord.Embed(color=color, title="*%s pouts*" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sumfuk(self, ctx):
        color, url = await self.weeb.sumfuk()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def initiald(self, ctx):
        color, url = await self.weeb.initial_d()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deredere(self, ctx):
        color, url = await self.weeb.deredere()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sleepy(self, ctx):
        color, url = await self.weeb.sleepy()
        em = discord.Embed(color=color, title="%s is sleepy 💤" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def shrug(self, ctx):
        color, url = await self.weeb.shrug()
        em = discord.Embed(color=color, title="*%s shrugs*" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hug(self, ctx, user: discord.Member):
        """Hug someone (> ^_^ )>"""
        if user == ctx.author:
            title = "*%s hugs themself*" % ctx.author.name
        else:
            title = "*%s hugs %s* (> ^_^ )>" % (ctx.author.name, user.name)

        color, url = await self.weeb.hug()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kiss(self, ctx, user: discord.Member):
        """Kiss someone >///<"""
        if user == ctx.author:
            title = "*%s kisses themself*" % ctx.author.name
        else:
            title = "*%s kisses %s* >///<" % (ctx.author.name, user.name)

        color, url = await self.weeb.kiss()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx, user: discord.Member):
        """*pat pat pat*"""
        if user == ctx.author:
            title = "*%s pats themself*" % ctx.author.name
        else:
            title = "*%s pats %s*" % (ctx.author.name, user.name)

        color, url = await self.weeb.pat()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cuddle(self, ctx, user: discord.Member):
        """Cuddle someone uwuw"""
        if user == ctx.author:
            title = "*%s cuddles themself*" % ctx.author.name
        else:
            title = "*%s cuddles %s* (>^_^)><(^o^<)" % (ctx.author.name, user.name)

        color, url = await self.weeb.cuddle()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def tickle(self, ctx, user: discord.Member):
        """Tickle someone >_<"""
        if user == ctx.author:
            title = "*%s tickles themself*" % ctx.author.name
        else:
            title = "*%s tickles %s* >_<" % (ctx.author.name, user.name)

        color, url = await self.weeb.tickle()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bite(self, ctx, user: discord.Member):
        if user == ctx.author:
            title = "*%s bit themself*" % ctx.author.name
        else:
            title = "*%s bites %s*" % (ctx.author.name, user.name)

        color, url = await self.weeb.bite()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slap(self, ctx, user: discord.Member):
        """Slap someone ;w;"""
        if user == ctx.author:
            title = "*%s slaps themself*" % ctx.author.name
        else:
            title = "*%s slaps %s*" % (ctx.author.name, user.name)

        color, url = await self.weeb.slap()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def punch(self, ctx, user: discord.Member):
        """Punch someone >_<"""
        if user == ctx.author:
            title = "*%s punches themself*" % ctx.author.name
        else:
            title = "*%s punches %s* (>^_^)><(^o^<)" % (ctx.author.name, user.name)

        color, url = await self.weeb.punch()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def poke(self, ctx, user: discord.Member):
        """Poke someone >///<"""
        if user == ctx.author:
            title = "*%s pokes themself*" % ctx.author.name
        else:
            title = "*%s pokes %s* >///<" % (ctx.author.name, user.name)

        color, url = await self.weeb.poke()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nom(self, ctx, user: discord.Member):
        """Nom!"""
        if user == ctx.author:
            title = "*%s noms on themself*" % ctx.author.name
        else:
            title = "*%s noms %s*" % (ctx.author.name, user.name)

        color, url = await self.weeb.nom()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lick(self, ctx, user: discord.Member):
        """*licks* >///<"""
        if user == ctx.author:
            title = "*%s licks themself*" % ctx.author.name
        else:
            title = "*%s licks %s*" % (ctx.author.name, user.name)

        color, url = await self.weeb.lick()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def greet(self, ctx, user: discord.Member):
        color, url = await self.weeb.greet()
        em = discord.Embed(color=color, title="%s greets %s!" % (ctx.author.name, user.name)).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lewd(self, ctx):
        """So l-lewd >///<"""
        color, url = await self.weeb.lewd()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def trap(self, ctx):
        color, url = await self.weeb.trap()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def owo(self, ctx):
        """OwO Whats This"""
        color, url = await self.weeb.owo()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wasted(self, ctx):
        color, url = await self.weeb.wasted()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def banghead(self, ctx):
        """*bangs head*"""
        color, url = await self.weeb.banghead()
        em = discord.Embed(color=color, title="*%s bangs their head*" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def discordmeme(self, ctx):
        color, url = await self.weeb.discord_memes()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def stare(self, ctx, user: discord.Member = None):
        """*Stares*"""
        if user:
            if user == ctx.author:
                title = "*%s stares at themself* 👀" % ctx.author.name
            else:
                title = "*%s stares at %s* 👀" % (ctx.author.name, user.name)
        else:
            title = "*%s stares* 👀" % ctx.author.name

        color, url = await self.weeb.stare()
        em = discord.Embed(color=color, title=title).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thinking(self, ctx):
        color, url = await self.weeb.thinking()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dab(self, ctx):
        """Dab dab dab"""
        color, url = await self.weeb.dab()
        em = discord.Embed(color=color, title="*%s dabs*" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command(aliases=["neko", "nko", "lewdneko", "nya"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kemonomimi(self, ctx):
        if not ctx.message.channel.is_nsfw():
            color, url = await self.weeb.kemonomimi()
            em = discord.Embed(color=color).set_image(url=url)
            await ctx.send(embed=em)
        else:
            url = randchoice(['https://nekos.life/api/v2/img/nsfw_neko_gif', 'https://nekos.life/api/v2/img/lewd'])
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    res = await r.json()
            url = res["url"]
            color = await self.weeb.get_dominant_color(url)
            em = discord.Embed(color=color).set_image(url=url)
            await ctx.send(embed=em)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(pass_context=True, aliases=['foxgirls'])
    async def foxgirl(self, ctx):
        """Fox Girls OwO"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/fox_girl') as r:
                res = await r.json()
        url = res["url"]
        color = await self.weeb.get_dominant_color(url)
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rem(self, ctx):
        color, url = await self.weeb.rem()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def triggered(self, ctx):
        color, url = await self.weeb.triggered()
        em = discord.Embed(color=color, title="%s is triggered" % ctx.author.name).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def poi(self, ctx):
        color, url = await self.weeb.poi()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deletthis(self, ctx):
        color, url = await self.weeb.delet_this()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def insultwaifu(self, ctx):
        data = await self.weeb.waifu_insult_gen(ctx.author.avatar_url_as(format="png"))
        await ctx.send(file=discord.File(fp=data, filename="insultwaifu.png"))

def setup(bot):
    bot.add_cog(TestWeeb(bot))
