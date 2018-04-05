from discord.ext import commands
import asyncio, config, dbl, discord, aiohttp, random, pymysql

connection = pymysql.connect(host="localhost",
                             user="root",
                             password="rektdiscord",
                             db="nekobot",
                             port=3306)
db = connection.cursor()

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
        await ctx.send("Starting DBL...")
        while True:
            print("Attempting to update server count.")
            try:
                db.execute("SELECT amount FROM stats WHERE type = \"messages\"")
                messages = int(db.fetchone()[0])
                db.execute(f"UPDATE stats SET amount = {int(self.bot.counter['messages_read'] + messages)} WHERE type = \"messages\"")
                db.execute("SELECT amount FROM stats WHERE type = \"commands\"")
                commands = int(db.fetchone()[0])
                db.execute(
                    f"UPDATE stats SET amount = {int(self.bot.counter['commands'] + commands)} WHERE type = \"messages\"")
                self.bot.counter['commands'] = 0
                stats2 = [f"Servers: {len(self.bot.guilds)}", f"Users: {len(set(self.bot.get_all_members()))}",
                          "OwO whats n!help", "🤔🤔🤔"]
                await self.dblpy.post_server_count(shard_count=self.bot.shard_count, shard_no=self.bot.shard_id)
                print("Posted server count. {}".format(len(self.bot.guilds)))
                game = discord.Streaming(name=random.choice(stats2), url="https://www.twitch.tv/rekt4lifecs")
                await self.bot.change_presence(activity=game)
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)

def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
