from discord.ext import commands
import discord, config, aiohttp
import base64, json
import os

class Games:

    def __init__(self, bot):
        self.bot = bot

    async def execute(self, query: str, isSelect: bool = False, fetchAll: bool = False, commit: bool = False):
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(query)
                if isSelect:
                    if fetchAll:
                        values = await db.fetchall()
                    else:
                        values = await db.fetchone()
                if commit:
                    await conn.commit()
            if isSelect:
                return values

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
        try:
            if await self.execute('SELECT 1 FROM osu WHERE userid = {}'.format(ctx.message.author.id), isSelect=True):
                await self.execute(f"UPDATE osu SET osu = \"{username}\" WHERE userid = {ctx.message.author.id}",
                                   commit=True)
                await ctx.send("Updated!")
            else:
                await self.execute(f"INSERT IGNORE INTO osu VALUES ({ctx.message.author.id}, \"{username}\")",
                           commit=True)
                await ctx.send("Added user!")
        except:
            await ctx.send("Failed to add user.")

    @osu.command()
    async def stats(self, ctx, user : discord.Member = None):
        """Show player stats"""
        if user == None:
            user = ctx.message.author
        if not await self.execute('SELECT 1 FROM osu WHERE userid = {}'.format(user.id), isSelect=True):
            await ctx.send("That user doesn't have a OSU user attached to your account. Use `n!osu add` to add a user.")
        else:
            x = await self.execute(f"SELECT osu FROM osu WHERE userid = {ctx.message.author.id}", isSelect=True)
            username = x[0]
            await ctx.send(f"Getting results for \"{username}\"")
            try:
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"http://osu.ppy.sh/api/get_user?k={config.osu_key}&u={username}") as r:
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

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pubg(self, ctx, region:str, username:str):
        """Get PUBG Stats"""
        await ctx.trigger_typing()
        try:
            regions = ["krjp", "jp", "na", "eu", "oc", "kakao", "sea", "sa", "as"]
            if region not in regions:
                em = discord.Embed(color=0xDEADBF, title="Error", description="Invalid Region Code.")
                return await ctx.send(embed=em)
            base = f"https://api.playbattlegrounds.com/shards/pc-{region}"
            headers = {"Authorization": f"Bearer {config.pubg}",
                       "Accept": "application/vnd.api+json"}
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"{base}/players?filter[playerNames]={username}", headers=headers) as r:
                    res = await r.read()
                    if r.status == 404:
                        em = discord.Embed(color=0xDEADBF, title="Error", description="User not found.")
                        return await ctx.send(embed=em)
                res = json.loads(res)
                lastmatch = res["data"][0]["relationships"]["matches"]["data"][0]["id"]
                if not os.path.exists(f"data/pubg-cache/{lastmatch}.json"):
                    async with cs.get(f"{base}/matches/{lastmatch}", headers=headers) as m:
                        matchdata = await m.read()
                        matchdata = json.loads(matchdata)
                        with open(f"data/pubg-cache/{lastmatch}.json", "w") as outfile:
                            json.dump(matchdata, outfile)
                else:
                    matchdata = json.load(open(f"data/pubg-cache/{lastmatch}.json"))
            for player in matchdata["included"]:
                if player["type"] == "participant":
                    if player["attributes"]["stats"]["playerId"] == res["data"][0]["id"]:
                        assists = player["attributes"]["stats"]["assists"]
                        damageDealt = player["attributes"]["stats"]["damageDealt"]
                        headshotKills = player["attributes"]["stats"]["headshotKills"]
                        heals = player["attributes"]["stats"]["heals"]
                        kills = player["attributes"]["stats"]["kills"]
                        longestKill = player["attributes"]["stats"]["longestKill"]
                        walkDistance = player["attributes"]["stats"]["walkDistance"]
                        winPlace = player["attributes"]["stats"]["winPlace"]
            em = discord.Embed(color=0xDEADBF, title=f"Last Game Stats for {username}")
            em.add_field(name="Kills", value=kills)
            em.add_field(name="Headshots", value=headshotKills)
            em.add_field(name="Assists", value=assists)
            em.add_field(name="Longest Kill", value=longestKill)
            em.add_field(name="Damage Dealt", value=damageDealt)
            em.add_field(name="Win Place", value=winPlace)
            em.add_field(name="Walk Distance", value=walkDistance)
            em.add_field(name="Heals", value=heals)
            await ctx.send(embed=em)
        except Exception as e:
            await ctx.send("Failed to get data, error: `{e}`")

    @commands.command()
    @commands.cooldown(1, 25, commands.BucketType.user)
    async def minecraft(self, ctx, username:str):
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as r:
                    res = await r.json()
            user_id = res['id']
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{user_id}") as r:
                    res = await r.json()
            data = base64.b64decode(res['properties'][0]['value'])
            data = json.loads(data)
            skin = data['textures']['SKIN']['url']
            embed = discord.Embed(color=0xDEADBF, title=f"User: {res['name']}")
            embed.set_image(url=skin)
            await ctx.send(embed=embed)
        except:
            await ctx.send("**Failed to get user**")

    # @commands.command(aliases=['ow'])
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def overwatch(self, ctx, battletag : str):
    #     """Gets a user's Overwatch Stats"""
    #     user = battletag.replace("#", "-")
    #     async with aiohttp.ClientSession() as cs:
    #         async with cs.get(f"https://ow-api.herokuapp.com/stats/pc/global/{user}") as r:
    #             res = await r.json()
    #
    #     if res == {}:
    #         await ctx.send("Incorrect battletag. (caps sensetive)")
    #         return
    #
    #     em = discord.Embed(color=0xF99E1A,
    #                        title=f"**{battletag}** | **{res['level']}**")
    #     em.set_thumbnail(url=res['portrait'])
    #     qp = res['stats']['game']['quickplay']
    #     comp = res['stats']['game']['competitive']
    #
    #     # Top heroes
    #     top_hero = res['stats']['top_heroes']['quickplay'][0]
    #     if top_hero['hero'] == "D.Va":
    #         top = f"D.Va <:0x02E000000000007A:422031403991957505> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Soldier 76":
    #         top = f"Solider 76 <:0x02E000000000006E:422031400972320768> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Widowmaker":
    #         top = f"Widowmaker <:0x02E000000000000A:422031372727746570> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Bastion":
    #         top = f"Bastion <:0x02E0000000000015:422031401064333312> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Mei":
    #         top = f"Mei <:0x02E00000000000DD:422031375806234654> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Mercy":
    #         top = f"Mercy <:0x02E0000000000004:422031393636352000> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Hanzo":
    #         top = f"Hanzo <:0x02E0000000000005:422031393737146368> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Reinhardt":
    #         top = f"Reinhardt <:0x02E0000000000007:422031401257271299> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Pharah":
    #         top = f"Reinhardt <:0x02E0000000000008:422031404340346880> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Moira":
    #         top = f"Moira <:0x02E00000000001A2:422031381833449482> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Lúcio":
    #         top = f"Lúcio <:0x02E0000000000079:422031405531529229> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Symmetra":
    #         top = f"Symmetra <:0x02E0000000000016:422031402557505536> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Sombra":
    #         top = f"Sombra <:0x02E000000000012E:422031404839337995> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Reaper":
    #         top = f"Reaper <:0x02E0000000000002:422031387869315082> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Tracer":
    #         top = f"Tracer <:0x02E0000000000003:422031388397666304> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Torbjörn":
    #         top = f"Torbjörn <:0x02E0000000000006:422031400976384021> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Winston":
    #         top = f"Winston <:0x02E0000000000009:422031403006558228> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Zenyatta":
    #         top = f"Zenyatta <:0x02E0000000000020:422031401014132737> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Genji":
    #         top = f"Genji <:0x02E0000000000029:422031405535461398> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Roadhog":
    #         top = f"Roadhog <:0x02E0000000000040:422031405757890560> - {top_hero['played']}"
    #     elif top_hero['hero'] == "McCree":
    #         top = f"McCree <:0x02E0000000000042:422031405816610816> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Junkrat":
    #         top = f"Junkrat <:0x02E0000000000065:422031404512182284> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Zarya":
    #         top = f"Zarya <:0x02E0000000000068:422031404973686794> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Doomfist":
    #         top = f"Doomfist <:0x02E000000000012F:422031400364015626> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Ana":
    #         top = f"Ana <:0x02E000000000013B:422031403971117067> - {top_hero['played']}"
    #     elif top_hero['hero'] == "Orisa":
    #         top = f"Orisa <:0x02E000000000013E:422031405833256960> - {top_hero['played']}"
    #
    #
    #     em.add_field(name="Quickplay", value=f"Time Played: **{qp[0]['value']}**\n"
    #                                          f"Games Won: **{qp[1]['value']}**\n"
    #                                          f"Medals: **{res['stats']['match_awards']['quickplay'][1]['value']}**")
    #     try:
    #         em.add_field(name="Competetive", value=f"Time Played: **{comp[0]['value']}**\n"
    #                                              f"Games Won: **{comp[1]['value']}**\n"
    #                                              f"Medals: **{res['stats']['match_awards']['competetive'][1]['value']}**")
    #     except: pass
    #     em.add_field(name="Top Hero", value=f"**{top}**")
    #
    #     await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Games(bot))
