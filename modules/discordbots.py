from discord.ext import commands
import asyncio, config, dbl, discord, random, aiohttp

messages = ["OwO Whats this", "MonkaS", "OwO", "Haiiiii", ".help", "🤔🤔🤔", "HMMM🤔", "USE n! WEW", "n!HELP REE"]

class DiscordBotsOrgAPI:
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = config.dbots_key
        self.dblpy = dbl.Client(self.bot, self.token)

    @commands.command()
    @commands.is_owner()
    async def startdbl(self, ctx):
        stats2 = [f"Servers: {len(self.bot.guilds)}", f"Users: {len(set(self.bot.get_all_members()))}",
                  "OwO whats n!help", "🤔🤔🤔"]
        await ctx.send("Starting DBL...")
        while True:
            print("Attempting to update server count.")
            try:
                await self.dblpy.post_server_count(shard_count=self.bot.shard_count, shard_no=self.bot.shard_id)
                print("Posted server count. {}".format(len(self.bot.guilds)))
                game = discord.Streaming(name=random.choice(stats2), url="https://www.twitch.tv/rekt4lifecs")
                await self.bot.change_presence(activity=game)
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post('https://bots.discord.pw/api/bots/310039170792030211/stats',
                                            headers={'Authorization': f'{config.dpw_key}'},
                                            data={"shard_count": self.bot.shard_count,
                                                  "server_count": len(self.bot.guilds)}) as response:
                        t = await response.json()
                        print(t)
            except Exception as e:
                print(f"Failed to post to pw, {e}")

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post('https://ls.terminal.ink/api/v1/bots/310039170792030211',
                                            headers={'Authorization': f'{config.terminal_key}'},
                                            data={"server_count": len(self.bot.guilds)}) as response:
                        t = await response.json()
                        print(t)
            except Exception as e:
                print(f"Failed to post to terminal, {e}")
            await asyncio.sleep(1800)

def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
