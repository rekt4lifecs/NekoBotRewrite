from discord.ext import commands
import discord
from .utils.weeb import Weeb
import config
import aiohttp
from random import choice as randchoice

# key = type
#   0 = self
#   1 = other
texts = {
    "handholding": [
        "*%s holds their own hand*",
        "*%s holds %s's hand* >///<"
    ],
    "bang": [
        "%s banged themself ;w;",
        "*%s bangs %s*"
    ],
    "insult": [
        "%s insulted themself ;w;",
        "*%s insulted %s*"
    ],
    "hug": [
        "*%s hugs themself*",
        "*%s hugs %s* (> ^_^ )>"
    ],
    "kiss": [
        "*%s kisses themself*",
        "*%s kisses %s* >///<"
    ],
    "pat": [
        "*%s pats themself*",
        "*%s pats %s*"
    ],
    "cuddle": [
        "*%s cuddles themself*",
        "*%s cuddles %s* (>^_^)><(^o^<)"
    ],
    "tickle": [
        "*%s tickles themself*",
        "*%s tickles %s* >_<"
    ],
    "bite": [
        "*%s bites themself*",
        "*%s bites %s*"
    ],
    "slap": [
        "*%s slaps themself*",
        "*%s slaps %s*"
    ],
    "punch": [
        "*%s punches themself*",
        "*%s punches %s*"
    ],
    "poke": [
        "*%s pokes themself*",
        "*%s pokes %s* >///<"
    ],
    "nom": [
        "*%s noms on themself*",
        "*%s noms %s*"
    ],
    "lick": [
        "*%s licks themself*",
        "*%s licks %s*"
    ],
    "stare": [
        "*%s stares* 👀",
        "*%s stares at %s* 👀"
    ]
}

class Reactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.weeb = Weeb(config.weeb, bot)

    # Guild only for all commnds
    async def cog_check(self, ctx):
        return True if ctx.guild else False

    async def _weeb_handler(self, ctx: commands.Context, arg, image: str):
        color, url = await (getattr(self.weeb, image))()
        em = discord.Embed()
        text = texts.get(image, "empty")
        try:
            arg = await (commands.MemberConverter()).convert(ctx=ctx, argument=arg)
        except commands.BadArgument:
            pass
        if isinstance(arg, discord.Member) and arg.id == ctx.author.id:
            em.title = text[0] % (ctx.author.name,)
        else:
            if isinstance(arg, discord.Member):
                name = arg.name
            else:
                name = arg[:30]
            em.title = text[1] % (ctx.author.name, name)
        em.color = color
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def awoo(self, ctx):
        """Awooo!"""
        color, url = await self.weeb.awoo()
        em = discord.Embed(color=color).set_image(url=url)
        await ctx.send(embed=em)

    @commands.command(aliases=["handholding"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def handhold(self, ctx, user):
        """Handhold >///<"""
        await self._weeb_handler(ctx, user, "handholding")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bang(self, ctx, user):
        """Bang someone pewpew"""
        await self._weeb_handler(ctx, user, "bang")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blush(self, ctx):
        """ohmy >///<"""
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
    async def insult(self, ctx, user):
        """Insult someone ;w;"""
        await self._weeb_handler(ctx, user, "insult")

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
        """EXPLOSION!"""
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
    async def hug(self, ctx, user):
        """Hug someone (> ^_^ )>"""
        await self._weeb_handler(ctx, user, "hug")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kiss(self, ctx, user):
        """Kiss someone >///<"""
        await self._weeb_handler(ctx, user, "kiss")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx, user):
        """*pat pat pat*"""
        await self._weeb_handler(ctx, user, "pat")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cuddle(self, ctx, user):
        """Cuddle someone uwuw"""
        await self._weeb_handler(ctx, user, "cuddle")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def tickle(self, ctx, user):
        """Tickle someone >_<"""
        await self._weeb_handler(ctx, user, "tickle")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bite(self, ctx, user):
        await self._weeb_handler(ctx, user, "bite")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slap(self, ctx, user):
        """Slap someone ;w;"""
        await self._weeb_handler(ctx, user, "slap")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def punch(self, ctx, user):
        """Punch someone >_<"""
        await self._weeb_handler(ctx, user, "punch")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def poke(self, ctx, user):
        """Poke someone >///<"""
        await self._weeb_handler(ctx, user, "poke")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nom(self, ctx, user):
        """Nom!"""
        await self._weeb_handler(ctx, user, "nom")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lick(self, ctx, user):
        """*licks* >///<"""
        await self._weeb_handler(ctx, user, "lick")

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
    async def stare(self, ctx, user=None):
        """*Stares*"""
        if user is None:
            color, url = await self.weeb.stare()
            return await ctx.send(embed=discord.Embed(color=color).set_image(url=url))
        await self._weeb_handler(ctx, user, "stare")

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
    @commands.guild_only()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def insultwaifu(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author
        data = await self.weeb.waifu_insult_gen(str(user.avatar_url_as(format="png")))
        await ctx.send(file=discord.File(fp=data, filename="insultwaifu.png"))

def setup(bot):
    bot.add_cog(Reactions(bot))
