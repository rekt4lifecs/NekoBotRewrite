from discord.ext import commands
import discord, config, aiohttp, random, requests
from collections import Counter
from io import BytesIO

key = config.weeb
auth = {"Authorization": "Wolke " + key}

class Reactions:
    """Reactions"""

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True)
    async def hug(self, ctx, user: discord.Member):
        """Hug someone OwO"""
        self.counter['hug'] += 1
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
        self.counter['kiss'] += 1
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
        self.counter['pat'] += 1
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
        self.counter['cuddle'] += 1
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
        self.counter['tickle'] += 1
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
        self.counter['bite'] += 1
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
        self.counter['slap'] += 1
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
        self.counter['punch'] += 1
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
        self.counter['poke'] += 1
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
        self.counter['nom'] += 1
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
        self.counter['lick'] += 1
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
        self.counter['greet'] += 1
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
        self.counter['lewd'] += 1
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
        self.counter['trap'] += 1
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
        self.counter['owo'] += 1
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
        self.counter['wasted'] += 1
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
        self.counter['banghead'] += 1
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
        self.counter['discordmeme'] += 1
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
        self.counter['stare'] += 1
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
        self.counter['thinking'] += 1
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
        self.counter['dab'] += 1
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=dab') as r:
                res = await r.json()
                em = discord.Embed(title="**{}** hits a thicc dab".format(ctx.message.author.name),
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True, aliases=["neko"])
    async def kemonomimi(self, ctx):
        """Girls with animal characteristics OwO"""
        self.counter['kemonomimi'] += 1
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=kemonomimi') as r:
                res = await r.json()
                em = discord.Embed(
                                   color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(pass_context=True, aliases=['foxgirls'])
    async def foxgirl(self, ctx):
        """Fox Girls OwO"""
        self.counter['fox_girl'] += 1
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
        self.counter['rem'] += 1
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
        self.counter['poi'] += 1
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
        self.counter['why'] += 1
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekos.life/api/v2/why") as r:
                res = await r.json()
                embed = discord.Embed(title="WHY!!", description="{}".format(res['why']), color=0xDEADBF)
                await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bang(self, ctx, user: discord.Member):
        """~BANG~"""
        self.counter['bang'] += 1
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
                await ctx.send(file=discord.File(fp='res.png'))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reactions(self, ctx):
        embed = discord.Embed(color=0xDEADBF,
                              title="Reaction Stats")
        embed.add_field(name="Hug", value=self.counter['hug'])
        embed.add_field(name="Kiss", value=self.counter['kiss'])
        embed.add_field(name="Pat", value=self.counter['pat'])
        embed.add_field(name="Cuddle", value=self.counter['cuddle'])
        embed.add_field(name="Tickle", value=self.counter['tickle'])
        embed.add_field(name="Bite", value=self.counter['bite'])
        embed.add_field(name="Slap", value=self.counter['slap'])
        embed.add_field(name="Punch", value=self.counter['punch'])
        embed.add_field(name="Nom", value=self.counter['nom'])
        embed.add_field(name="Lick", value=self.counter['lick'])
        embed.add_field(name="lewd", value=self.counter['lewd'])
        embed.add_field(name="Trap", value=self.counter['trap'])
        embed.add_field(name="OwO", value=self.counter['owo'])
        embed.add_field(name="Wasted", value=self.counter['wasted'])
        embed.add_field(name="Banghead", value=self.counter['banghead'])
        embed.add_field(name="DiscordMeme", value=self.counter['discordmeme'])
        embed.add_field(name="Stare", value=self.counter['stare'])
        embed.add_field(name="Thinking", value=self.counter['thinking'])
        embed.add_field(name="Dab", value=self.counter['dab'])
        embed.add_field(name="Kemonomimi", value=self.counter['kemonomimi'])
        embed.add_field(name="Why", value=self.counter['why'])
        embed.add_field(name="Greet", value=self.counter['greet'])
        embed.add_field(name="Poi", value=self.counter['poi'])
        embed.add_field(name="Rem", value=self.counter['rem'])
        embed.add_field(name="Fox Girls", value=self.counter['fox_girl'])

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Reactions(bot))