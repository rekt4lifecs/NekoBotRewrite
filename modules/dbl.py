from discord.ext import commands
import asyncio, config, dbl

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
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)

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