from discord.ext import commands
import discord, pymysql, config
from .utils import checks

connection = pymysql.connect(user=config.db.user,
                             password=config.db.password,
                             host=config.db.host,
                             port=config.db.port,
                             database=config.db.database)
db = connection.cursor()

class Reports:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_in_guilds()
    async def report(self, ctx, *, report : str):
        """Report System for Mods"""
        user = ctx.message.author
        if '"' in report:
            print(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "'" in report:
            print(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif ";" in report:
            print(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        if report.startswith("close"):
            if checks.is_mod():
                if not db.execute('SELECT 1 FROM reports WHERE userid = {}'.format(report[6:])):
                    await ctx.send("This user does not have a open report.")
                    return
                else:
                    db.execute(f"DELETE FROM reports WHERE userid = {report[:6]}")
                    connection.commit()
                    await ctx.send(f"User report {report[:6]} closed.")
                    return
            else:
                await ctx.send("You are not a mod.")
                return
        else:
            if db.execute('SELECT 1 FROM reports WHERE userid = {}'.format(user.id)):
                await ctx.send("You already have a report open. Wait for the first report to close.")
                return
            else:
                try:
                    db.execute()
                    connection.commit()
                    await ctx.send("Sent report.")

def setup(bot):
    bot.add_cog(Reports(bot))