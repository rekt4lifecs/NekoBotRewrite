from discord.ext import commands
import asyncio, config, dbl, discord, aiohttp, random

messages = ["OwO Whats this", "MonkaS", "OwO", "Haiiiii", ".help", "🤔🤔🤔", "HMMM🤔"]


class DiscordBotsOrgAPI:
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = config.dbots.key
        self.dblpy = dbl.Client(self.bot, self.token)

    @commands.command()
    @commands.is_owner()
    async def startdbl(self, ctx):
        await ctx.send("Starting DBL...")
        while True:
            print("Attempting to update server count.")
            try:
                await self.dblpy.post_server_count(shard_count=self.bot.shard_count, shard_no=self.bot.shard_id)
                print("Posted server count. {}".format(len(self.bot.guilds)))
                game = discord.Game(type=1, url="https://www.twitch.tv/rekt4lifecs", name=random.choice(messages))
                await self.bot.change_presence(game=game)
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            try:
                async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key2}) as session:
                    url = 'https://bots.discord.pw/api/bots/310039170792030211/stats'
                    await session.post(url, data={"shard_id": self.bot.shard_id, "shard_count": self.bot.shard_count,
                                                  "server_count": len(self.bot.guilds)})
            except Exception as e:
                print("Failed to post discord.bots.pw\n{}".format(e))
            await asyncio.sleep(1800)

    @commands.command()
    async def botinfo(self, ctx, bot_user : int = None):
        """Get Bot Info"""
        if bot_user == None:
            bot_user = config.botid
        url = "https://discordbots.org/api/bots/310039170792030211"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                bot = await r.json()

        em = discord.Embed(color=0xDEADBF, title=bot['username'] + bot['discriminator'], description=bot['shortdesc'])
        em.add_field(name="Prefix", value=bot['prefix'])
        em.add_field(name="Lib", value=bot['lib'])
        em.add_field(name="Owners", value=f"<@{bot['owners'][0]}>")
        em.add_field(name="Votes", value=bot['points'])
        em.add_field(name="Server Count", value=bot['server_count'])
        em.add_field(name="ID", value=bot['id'])
        em.add_field(name="Certified", value=bot['certifiedBot'])
        em.add_field(name="GitHub", value=bot['github'])
        em.add_field(name="Website", value=bot['website'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.is_owner()
    async def dblcheck(self, ctx):
        url = "https://discordbots.org/api/bots/310039170792030211/votes"
        async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
            async with cs.get(url) as r:
                res = await r.json()
        for x in res:
            if str(x['id']) == str(ctx.message.author.id):
                await ctx.send("True")
                break
        else:
            await ctx.send("False")

    # @commands.command()
    # @commands.is_owner()
    # async def updatedbl(self, ctx):
    #     await ctx.send("Attempting to update...")
    #     try:
    #         await self.dblpy.post_server_count()
    #         await ctx.send('posted server count ({})'.format(len(self.bot.guilds)))
    #     except Exception as e:
    #         await ctx.send("Failed,\n{}".format(e))


def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
