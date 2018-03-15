from discord.ext import commands
import discord, pymysql, config, aiohttp

connection = pymysql.connect(user='root',
                             password=config.dbpass,
                             host='localhost',
                             port=3306,
                             database='nekobot')
db = connection.cursor()

class Games:

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

    @commands.command(aliases=['ow'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def overwatch(self, ctx, battletag : str):
        """Gets a user's Overwatch Stats"""
        user = battletag.replace("#", "-")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://ow-api.herokuapp.com/stats/pc/global/{user}") as r:
                res = await r.json()

        if res == {}:
            await ctx.send("Incorrect battletag. (caps sensetive)")
            return

        em = discord.Embed(color=0xF99E1A,
                           title=f"**{battletag}** | **{res['level']}**")
        em.set_thumbnail(url=res['portrait'])
        qp = res['stats']['game']['quickplay']
        comp = res['stats']['game']['competitive']

        # Top heroes
        top_hero = res['stats']['top_heroes']['quickplay'][0]
        if top_hero['hero'] == "D.Va":
            top = f"D.Va <:0x02E000000000007A:422031403991957505> - {top_hero['played']}"
        elif top_hero['hero'] == "Soldier 76":
            top = f"Solider 76 <:0x02E000000000006E:422031400972320768> - {top_hero['played']}"
        elif top_hero['hero'] == "Widowmaker":
            top = f"Widowmaker <:0x02E000000000000A:422031372727746570> - {top_hero['played']}"
        elif top_hero['hero'] == "Bastion":
            top = f"Bastion <:0x02E0000000000015:422031401064333312> - {top_hero['played']}"
        elif top_hero['hero'] == "Mei":
            top = f"Mei <:0x02E00000000000DD:422031375806234654> - {top_hero['played']}"
        elif top_hero['hero'] == "Mercy":
            top = f"Mercy <:0x02E0000000000004:422031393636352000> - {top_hero['played']}"
        elif top_hero['hero'] == "Hanzo":
            top = f"Hanzo <:0x02E0000000000005:422031393737146368> - {top_hero['played']}"
        elif top_hero['hero'] == "Reinhardt":
            top = f"Reinhardt <:0x02E0000000000007:422031401257271299> - {top_hero['played']}"
        elif top_hero['hero'] == "Pharah":
            top = f"Reinhardt <:0x02E0000000000008:422031404340346880> - {top_hero['played']}"
        elif top_hero['hero'] == "Moira":
            top = f"Moira <:0x02E00000000001A2:422031381833449482> - {top_hero['played']}"
        elif top_hero['hero'] == "Lúcio":
            top = f"Lúcio <:0x02E0000000000079:422031405531529229> - {top_hero['played']}"
        elif top_hero['hero'] == "Symmetra":
            top = f"Symmetra <:0x02E0000000000016:422031402557505536> - {top_hero['played']}"
        elif top_hero['hero'] == "Sombra":
            top = f"Sombra <:0x02E000000000012E:422031404839337995> - {top_hero['played']}"
        elif top_hero['hero'] == "Reaper":
            top = f"Reaper <:0x02E0000000000002:422031387869315082> - {top_hero['played']}"
        elif top_hero['hero'] == "Tracer":
            top = f"Tracer <:0x02E0000000000003:422031388397666304> - {top_hero['played']}"
        elif top_hero['hero'] == "Torbjörn":
            top = f"Torbjörn <:0x02E0000000000006:422031400976384021> - {top_hero['played']}"
        elif top_hero['hero'] == "Winston":
            top = f"Winston <:0x02E0000000000009:422031403006558228> - {top_hero['played']}"
        elif top_hero['hero'] == "Zenyatta":
            top = f"Zenyatta <:0x02E0000000000020:422031401014132737> - {top_hero['played']}"
        elif top_hero['hero'] == "Genji":
            top = f"Genji <:0x02E0000000000029:422031405535461398> - {top_hero['played']}"
        elif top_hero['hero'] == "Roadhog":
            top = f"Roadhog <:0x02E0000000000040:422031405757890560> - {top_hero['played']}"
        elif top_hero['hero'] == "McCree":
            top = f"McCree <:0x02E0000000000042:422031405816610816> - {top_hero['played']}"
        elif top_hero['hero'] == "Junkrat":
            top = f"Junkrat <:0x02E0000000000065:422031404512182284> - {top_hero['played']}"
        elif top_hero['hero'] == "Zarya":
            top = f"Zarya <:0x02E0000000000068:422031404973686794> - {top_hero['played']}"
        elif top_hero['hero'] == "Doomfist":
            top = f"Doomfist <:0x02E000000000012F:422031400364015626> - {top_hero['played']}"
        elif top_hero['hero'] == "Ana":
            top = f"Ana <:0x02E000000000013B:422031403971117067> - {top_hero['played']}"
        elif top_hero['hero'] == "Orisa":
            top = f"Orisa <:0x02E000000000013E:422031405833256960> - {top_hero['played']}"


        em.add_field(name="Quickplay", value=f"Time Played: **{qp[0]['value']}**\n"
                                             f"Games Won: **{qp[1]['value']}**\n"
                                             f"Medals: **{res['stats']['match_awards']['quickplay'][1]['value']}**")
        try:
            em.add_field(name="Competetive", value=f"Time Played: **{comp[0]['value']}**\n"
                                                 f"Games Won: **{comp[1]['value']}**\n"
                                                 f"Medals: **{res['stats']['match_awards']['competetive'][1]['value']}**")
        except: pass
        em.add_field(name="Top Hero", value=f"**{top}**")

        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Games(bot))