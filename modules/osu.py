from discord.ext import commands
import discord, pymysql, config, aiohttp

connection = pymysql.connect(user=config.db.user,
                             password=config.db.password,
                             host=config.db.host,
                             port=config.db.port,
                             database=config.db.database)
db = connection.cursor()

class OSU:
    """OSU for NekoBot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def osu(self, ctx):
        """OSU Stats"""
        if not ctx.invoked_subcommand or None:
            embed = discord.Embed(color=0xDEADBF,
                                  title="OSU",
                                  description="n!osu add - **Add player profile**\n"
                                              "n!osu stats - **Show player stats**")
            await ctx.send(embed=embed)

    @osu.command()
    async def add(self, ctx, username : str):
        """Add OSU Account"""
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

    @osu.command()
    async def stats(self, ctx, user : discord.Member = None):
        """Show player stats"""
        if user == None:
            user = ctx.message.author
        if not db.execute('SELECT 1 FROM osu WHERE userid = {}'.format(user.id)):
            await ctx.send("That user doesn't have a OSU user attached to your account. Use `n!osu add` to add a user.")
        else:
            db.execute(f"SELECT osu FROM osu WHERE userid = {ctx.message.author.id}")
            username = db.fetchone()[0]
            await ctx.send(f"Getting results for \"{username}\"")
            try:
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"http://osu.ppy.sh/api/get_user?k={config.osu.key}&u={username}") as r:
                        osu = await r.json()
                        if osu == []:
                            await ctx.send("Incorrect Username.")
                            return
                embed = discord.Embed(color=0xDEADBF,
                                      title=f"{username}")
                embed.add_field(name="Play Count", value=osu[0]['playcount'])
                embed.add_field(name="Ranked Score", value=osu[0]['ranked_score'])
                embed.add_field(name="Total Score", value=osu[0]['total_score'])
                embed.add_field(name="Level", value="%.2f" % float(osu[0]['level']))
                embed.add_field(name="Accuracy", value="%.2f" % float(osu[0]['accuracy']))
                embed.add_field(name="Country Ranking", value=osu[0]['pp_country_rank'])
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(color=0xDEADBF,
                                      title="Error Contacting OSU API",
                                      description=f"```{e}```")
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OSU(bot))