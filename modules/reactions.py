from discord.ext import commands
import discord, config, aiohttp
from collections import Counter
import random

key = config.weeb
auth = {"Authorization": "Wolke " + key,
        "User-Agent": "NekoBot/4.2.0"}

class Reactions:
    """Reactions"""

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def awoo(self, ctx):
        """AWOOOOOOOO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=awoo') as r:
                res = await r.json()
                em = discord.Embed(title="AWOOOO",
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def blush(self, ctx):
        """>~<"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=blush') as r:
                res = await r.json()
                em = discord.Embed(title=f"{ctx.message.author.name} blushes",
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def confused(self, ctx):
        """?!??!?!?"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=clagwimoth') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def dance(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=dance') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def insult(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=dance') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def cry(self, ctx):
        """;w;"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=cry') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def jojo(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=jojo') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def megumin(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=megumin') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def pout(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=pout') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def sumfuk(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=sumfuk') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def initiald(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=initial_d') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def deredere(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=deredere') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def sleepy(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=sleepy') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def shrug(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=shrug') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def hug(self, ctx, user: discord.Member):
        """Hug someone OwO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=hug') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "NekoBot"
                    text = "<:nekoHug:413608646988005376>"
                else:
                    user = user.name
                    text = "(=^‥^=) <a:nekoHuggu:413610309920489472>"
                em = discord.Embed(title="**{}** hugged **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def kiss(self, ctx, user: discord.Member):
        """Kiss someone OwO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=kiss') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "their arm ;-;"
                    text = ""
                else:
                    user = user.name
                    text = "❤(´ω｀*) <a:nekoKiss:413608424840888331>"
                em = discord.Embed(title="**{}** kissed **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def pat(self, ctx, user: discord.Member):
        """Pat someone OwO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=pat') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself ;-;"
                    text = ""
                else:
                    user = user.name
                    text = "(●ↀωↀ●) <a:nekoPat:413613223435042826>"
                em = discord.Embed(title="**{}** patted **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def cuddle(self, ctx, user: discord.Member):
        """Cudddddduuulzzzz OWO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=cuddle') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself ;-;"
                    text = ""
                else:
                    user = user.name
                    text = "OwO"
                em = discord.Embed(title="**{}** cudddddllllllzzzzz **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tickle(self, ctx, user: discord.Member):
        """Whats this OWO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=tickle') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself :3"
                    text = ""
                else:
                    user = user.name
                    text = ""
                em = discord.Embed(title="**{}** tickles **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bite(self, ctx, user: discord.Member):
        """Bite someone OwO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=bite') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself and cries ;-;"
                    text = ""
                else:
                    user = user.name
                    text = ""
                em = discord.Embed(title="**{}** bites **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def slap(self, ctx, user: discord.Member):
        """Ouch ;-;"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=slap') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself ;-;"
                    text = ""
                else:
                    user = user.name
                    text = "OwO"
                em = discord.Embed(title="**{}** slaps **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def punch(self, ctx, user: discord.Member):
        """Ouch ;-;"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=punch') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself ;-;"
                    text = ""
                else:
                    user = user.name
                    text = "Ouchh"
                em = discord.Embed(title="**{}** punches **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def poke(self, ctx, user: discord.Member):
        """poke poke poke ^-^"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=poke') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself"
                    text = ""
                else:
                    user = user.name
                    text = "UwU"
                em = discord.Embed(title="**{}** pokes **{}** {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def nom(self, ctx, user: discord.Member):
        """noomss on someone owo"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=nom') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "their leg"
                    text = ""
                else:
                    user = user.name
                    text = "... Delicious UwU"
                em = discord.Embed(title="**{}** noms **{}**{}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def lick(self, ctx, user: discord.Member):
        """licks someone"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=lick') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = " their eye"
                    text = ""
                else:
                    user = user.name
                    text = "... Mmmm, salty OwO"
                em = discord.Embed(title="**{}** licks **{}**{}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def greet(self, ctx, user: discord.Member):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=greet') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = " themself"
                    text = ""
                else:
                    user = user.name
                    text = " UwU"
                em = discord.Embed(title="**{}** greets **{}**{}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def lewd(self, ctx):
        """Leeewd!!!"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=lewd') as r:
                res = await r.json()
                em = discord.Embed(title="LEWD!!",
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def trap(self, ctx):
        """its a trap owo"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=trap') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def owo(self, ctx):
        """OwO Whats This"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=owo') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def wasted(self, ctx):
        """Wastteeddd"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=wasted') as r:
                res = await r.json()
                em = discord.Embed(title="**{}** is wasted".format(ctx.message.author.name),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def banghead(self, ctx):
        """Head banging intensifys"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=banghead') as r:
                res = await r.json()
                em = discord.Embed(title="**{}** bangs their head".format(ctx.message.author.name),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def discordmeme(self, ctx):
        """Discord Memes OwO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=discord_memes') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def stare(self, ctx):
        """Stares"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=stare') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def thinking(self, ctx):
        """THINKSSSS"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=thinking') as r:
                res = await r.json()
                em = discord.Embed(title="{} is thinking...".format(ctx.message.author.name),color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def dab(self, ctx):
        """hits a thicc dab"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=dab') as r:
                res = await r.json()
                em = discord.Embed(title="**{}** hits a thicc dab".format(ctx.message.author.name),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(pass_context=True, aliases=["neko", "nko", "lewdneko"])
    async def kemonomimi(self, ctx):
        """Girls with animal characteristics OwO"""
        if not ctx.message.channel.is_nsfw():
            async with aiohttp.ClientSession(headers=auth) as cs:
                async with cs.get(f'https://api.weeb.sh/images/random?type={random.choice(["kemonomimi", "neko"])}') as r:
                    res = await r.json()
                    em = discord.Embed(
                                       color=0xDEADBF)
                    em.set_image(url=res['url'])
                    await ctx.send(embed=em)
        else:
            async with aiohttp.ClientSession() as cs:
                x = random.choice(['https://nekos.life/api/v2/img/nsfw_neko_gif', 'http://nekos.life/api/lewd/neko'])
                async with cs.get(x) as r:
                    res = await r.json()
                    em = discord.Embed(color=0xDEADBF)
                    try:
                        urla = res['neko']
                    except:
                        urla = res['url']
                    em.set_image(url=urla)
                    em.set_footer(text="nekos.life owo")
                    await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True, aliases=['foxgirls'])
    async def foxgirl(self, ctx):
        """Fox Girls OwO"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://nekos.life/api/v2/img/fox_girl') as r:
                res = await r.json()
                em = discord.Embed(
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def rem(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=rem') as r:
                res = await r.json()
                em = discord.Embed(
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def poi(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=poi') as r:
                res = await r.json()
                em = discord.Embed(
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def why(self, ctx):
        """Why just why"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekos.life/api/v2/why") as r:
                res = await r.json()
                embed = discord.Embed(title="WHY!!", description="{}".format(res['why']), color=0xDEADBF)
                await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bang(self, ctx, user: discord.Member):
        """~BANG~"""
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=bang') as r:
                res = await r.json()
                if user == ctx.message.author:
                    user = "themself"
                    text = ""
                else:
                    user = user.name
                    text = "OOF"
                em = discord.Embed(title="**{}** shot **{}**, {}".format(ctx.message.author.name, user, text),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def insultwaifu(self, ctx, user : discord.Member = None):
        """Insult Waifu"""
        if user is None:
            user = ctx.message.author
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.weeb.sh/auto-image/waifu-insult',
                                    headers={'Authorization': f'Wolke {config.weeb}'},
                                    data={'avatar': user.avatar_url}) as response:
                t = await response.read()
                with open("res.png", "wb") as f:
                    f.write(t)
                await ctx.send(file=discord.File(fp='res.png'),
                               embed=discord.Embed(color=0xDEADBF).set_image(url="attachment://res.png"))

def setup(bot):
    bot.add_cog(Reactions(bot))