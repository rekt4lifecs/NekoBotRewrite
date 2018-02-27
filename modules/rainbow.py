from discord.ext import commands
import discord, pymysql, config

connection = pymysql.connect(user=config.db.user,
                             password=config.db.password,
                             host=config.db.host,
                             port=config.db.port,
                             database=config.db.database)
db = connection.cursor()

class Rainbow:
    """Rainbow6 Stats"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="r6")
    async def _rainbowsix(self, ctx):
        """Rainbow 6 Stats"""
        if not ctx.invoked_subcommand or None:
            embed = discord.Embed(color=0xDEABF,
                                  title="Rainbow 6",
                                  description=".r6 add - **Add a player profile**\n"
                                              ".r6 stats - **Show r6 Stats**")
            await ctx.send(embed=embed)

    @_rainbowsix.command()
    async def add(self, ctx, username : str):
        """Add a player profile"""
        if '"' in username:
            print(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "'" in username:
            print(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif ";" in username:
            print(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        if db.execute('SELECT 1 FROM osu WHERE userid = {}'.format(ctx.message.author.id)):
            db.execute(f"UPDATE osu SET osu = \"{username}\" WHERE userid = {ctx.message.author.id}")
            connection.commit()
            await ctx.send("Updated!")
        else:
            db.execute(f"INSERT IGNORE INTO osu VALUES ({ctx.message.author.id}, \"{username}\")")
            connection.commit()
            await ctx.send("Added user!")

def setup(bot):
    bot.add_cog(Rainbow(bot))