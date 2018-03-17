from discord.ext import commands
import discord, aiohttp, pymysql, asyncio, time, datetime, config, random, math, logging

connection = pymysql.connect(host="localhost",
                             user="root",
                             password="rektdiscord",
                             db="nekobot",
                             port=3306)
db = connection.cursor()

log = logging.getLogger("NekoBot")

class economy:
    """Economy"""

    def __init__(self, bot):
        self.bot = bot

    async def usercheck(self, datab : str, user : discord.Member):
        user = user.id
        if not db.execute(f'SELECT 1 FROM {datab} WHERE userid = {user}'):
            return False
        else:
            return True

    def _required_exp(self, level: int):
        if level < 0:
            return 0
        return 139 * level + 65

    def _level_exp(self, level: int):
        return level * 65 + 139 * level * (level - 1) // 2

    def _find_level(self, total_exp):
        return int((1 / 278) * (9 + math.sqrt(81 + 1112 * (total_exp))))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bank(self, ctx):
        """Bank info"""
        db.execute("SELECT balance FROM economy")

        total = 0
        amount_eco = db.execute("SELECT balance FROM economy")
        all_eco = db.fetchall()
        for x in all_eco:
            total = total + int(x[0])

        em = discord.Embed(color=0xDEADBF,
                           title="Welcome to the NekoBank!")
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.add_field(name="Total $", value=f"{total}")
        em.add_field(name="Registered Users", value=f"{amount_eco}")
        em.add_field(name="Total Users with XP", value=f"{db.execute('SELECT userid FROM levels')}")

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def register(self, ctx):
        """Register a bank account"""
        user = ctx.message.author

        if await self.usercheck('economy', user) is False:
            await ctx.send("Registered a bank account!")
            db.execute(f"INSERT INTO economy VALUES ({user.id}, 0, 0)")
            connection.commit()
        else:
            await ctx.send(f"You already have a bank account <:nkoDed:422666465238319107>")


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, user : discord.Member = None):
        """Get user's profile"""
        if user == None:
            user = ctx.message.author
        if await self.usercheck('levels', user) is False:
            rep = 0
            level = 0
            xp = 0
            required = 0
            description = ""
        else:
            db.execute(f"SELECT rep, level, info FROM levels WHERE userid = {user.id}")
            fetchlvl = db.fetchone()
            rep = fetchlvl[0]
            xp = fetchlvl[1]
            description = fetchlvl[2]
            level = self._find_level(xp)
            required = self._level_exp(level + 1)
        if await self.usercheck('marriage', user) is False:
            married = "Nobody"
        else:
            db.execute(f"SELECT marryid FROM marriage WHERE userid = {user.id}")
            marryid = int(db.fetchone()[0])
            married = await self.bot.get_user_info(marryid)
        if await self.usercheck('economy', user):
            db.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
            balance = int(db.fetchone()[0])
        else:
            balance = 0
        embed = discord.Embed(color=0xDEABDF, title=f"{user.display_name}'s Profile",
                              description=f"`Balance:` **{balance}**\n"
                                          f"`Rep:` **{rep}**\n"
                                          f"`Level:` **{level}** | **{xp}/{required}**\n\n"
                                          f"```\n{description}```\n"
                                          f"Married to: **{married}**")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['payday'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def daily(self, ctx):
        """Receive your daily bonus"""
        user = ctx.message.author
        if await self.usercheck('economy', user) is False:
            await ctx.send("You don't have a bank account...")
            return
        else:
            db.execute(f"SELECT payday FROM economy WHERE userid = {user.id}")
            paydaytime = db.fetchone()[0]
            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(int(paydaytime)).strftime("%d")
            if timecheck == timenow:
                tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1),
                                                     hour=0, minute=0, second=0)
                delta = tomorrow - datetime.datetime.now()
                timeleft = time.strftime("%H", time.gmtime(delta.seconds))
                await ctx.send(f"Wait another {timeleft} hours before using daily again...")
                return
            else:
                db.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
                balance = int(db.fetchone()[0])

                # Voter Bonus
                url = "https://discordbots.org/api/bots/310039170792030211/votes"
                async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
                    async with cs.get(url) as r:
                        res = await r.json()
                for x in res:
                    if str(x['id']) == str(ctx.message.author.id):
                        db.execute(f"UPDATE economy SET balance = {balance + 7500} WHERE userid = {user.id}")
                        connection.commit()
                        db.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}")
                        connection.commit()
                        embed = discord.Embed(color=0xDEADBF,
                                              title="Daily Credits",
                                              description="Recieved 2500 + 5000 Daily credits - Voter Bonus!")
                        await ctx.send(embed=embed)
                        break
                else:
                    db.execute(f"UPDATE economy SET balance = {balance + 2500} WHERE userid = {user.id}")
                    connection.commit()
                    db.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}")
                    connection.commit()
                    embed = discord.Embed(color=0xDEADBF,
                                          title="Daily Credits",
                                          description="Recieved 2500 Daily credits!")
                    embed.set_footer(text="Pssst voting will give you 3 times the daily bonus OwO, vote with n!vote")
                    await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rep(self, ctx, user : discord.Member):
        """Give user reputation"""
        author = ctx.message.author
        if user == author:
            await ctx.send("You can't give yourself rep <:nkoDed:422666465238319107>")
            return
        elif user.bot:
            await ctx.send("You can't rep bots <:nkoDed:422666465238319107>")
            return
        else:
            if await self.usercheck("levels", user) is False:
                await ctx.send("That user doesn't have an account yet")
                return
            else:
                db.execute(f"SELECT lastrep FROM levels WHERE userid = {author.id}")
                lastrep = db.fetchone()[0]
                timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
                timecheck = datetime.datetime.utcfromtimestamp(int(lastrep)).strftime("%d")
                if timecheck == timenow:
                    await ctx.send("You already used your rep today 😦")
                    return
                else:
                    db.execute(f"SELECT rep FROM levels WHERE userid = {user.id}")
                    current_rep = int(db.fetchone()[0])
                    db.execute(f"UPDATE levels SET rep = {current_rep + 1} WHERE userid = {user.id}")
                    connection.commit()
                    db.execute(f"UPDATE levels SET lastrep = {int(time.time())} WHERE userid = {author.id}")
                    connection.commit()
                    await ctx.send(f"{ctx.message.author.name} gave {user.mention} rep! 🎉🎉🎉")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setdesc(self, ctx, *, desc : str):
        """Set profile description"""
        if await self.usercheck("levels", ctx.message.author) is False:
            await ctx.send("Error finding your profile.")
            return
        if '"' in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "'" in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif ";" in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "%" in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif '\"' in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif '\\0' in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "\\'" in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "\%'" in desc:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        if len(desc) > 25:
            await ctx.send("Over character limit.")
            return
        else:
            db.execute(f"UPDATE levels SET info = \"{desc}\" WHERE userid = {ctx.message.author.id}")
            connection.commit()
            await ctx.send("Updated description!")

    @commands.command(aliases=['del'])
    @commands.is_owner()
    async def poof(self, ctx, id : int):
        db.execute(f"DELETE FROM levels WHERE userid = {id}")
        connection.commit()
        ctx.send(f"Deleted {id}")

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, sql: str):
        """Inject SQL"""
        try:
            db.execute(sql)
            connection.commit()
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send(f"`{e}`")

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def coinflip(self, ctx, amount : int):
        """Coinflip OwO"""
        user = ctx.message.author
        if amount <= 0:
            await ctx.send("Your amount is too low <:nkoDed:422666465238319107>")
            return
        elif amount > 5000:
            await ctx.send("You can't go past 5,000")
            return
        if await self.usercheck('economy', user) is False:
            await ctx.send("You don't have a bank account.")
            return
        else:
            db.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
            balance = int(db.fetchone()[0])
            if (balance - amount) < 0:
                await ctx.send("You don't have that much to spend...")
                return
            else:
                msg = await ctx.send("Flipping...")
                await asyncio.sleep(random.randint(2, 5))
                db.execute(f"UPDATE economy SET balance = {balance - amount} WHERE userid = {user.id}")
                connection.commit()
                choice = random.randint(0, 1)
                if choice == 1:
                    try:
                        await ctx.message.add_reaction('🎉')
                    except:
                        pass
                    em = discord.Embed(color=0x42FF73, description=f"{user.mention} Won {amount * 1.5}!!!")
                    await msg.edit(embed=em)
                    db.execute(f"UPDATE economy SET balance = {balance + int(amount * 1.5)} WHERE userid = {user.id}")
                    connection.commit()
                else:
                    em = discord.Embed(color=0xFF5637, description="You Lost 😦")
                    await msg.edit(embed=em)
                    try:
                        await ctx.message.add_reaction('😦')
                    except:
                        pass

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def top(self, ctx):
        # await self.bot.get_user_info(310039170792030211)
        msg = await ctx.send(embed=discord.Embed(color=0xDEADBF, title="Top Users", description="Loading..."))
        starttime = int(time.time())
        msg
        db.execute("SELECT userid, level FROM levels ORDER BY level DESC LIMIT 10")
        all_users = db.fetchall()
        try:
            user1 = await self.bot.get_user_info(int(all_users[0][0]))
        except:
            user1 = "Deleted User"
        user1_lvl = self._find_level(int(all_users[0][1]))
        try:
            user2 = await self.bot.get_user_info(int(all_users[1][0]))
        except:
            user2 = "Deleted User"
        user2_lvl = self._find_level(int(all_users[1][1]))
        try:
            user3 = await self.bot.get_user_info(int(all_users[2][0]))
        except:
            user3 = "Deleted User"
        user3_lvl = self._find_level(int(all_users[2][1]))
        try:
            user4 = await self.bot.get_user_info(int(all_users[3][0]))
        except:
            user4 = "Deleted User"
        user4_lvl = self._find_level(int(all_users[3][1]))
        try:
            user5 = await self.bot.get_user_info(int(all_users[4][0]))
        except:
            user5 = "Deleted User"
        user5_lvl = self._find_level(int(all_users[4][1]))
        try:
            user6 = await self.bot.get_user_info(int(all_users[5][0]))
        except:
            user6 = "Deleted User"
        user6_lvl = self._find_level(int(all_users[5][1]))
        try:
            user7 = await self.bot.get_user_info(int(all_users[6][0]))
        except:
            user7 = "Deleted User"
        user7_lvl = self._find_level(int(all_users[6][1]))
        try:
            user8 = await self.bot.get_user_info(int(all_users[7][0]))
        except:
            user8 = "Deleted User"
        user8_lvl = self._find_level(int(all_users[7][1]))
        try:
            user9 = await self.bot.get_user_info(int(all_users[8][0]))
        except:
            user9 = "Deleted User"
        user9_lvl = self._find_level(int(all_users[8][1]))
        try:
            user10 = await self.bot.get_user_info(int(all_users[9][0]))
        except:
            user10 = "Deleted User"
        user10_lvl = self._find_level(int(all_users[9][1]))

        embed = discord.Embed(color=0xDEADBF, title="Top Users",
                              description=f"`1. ♔{user1}♔ ({all_users[0][0]}) - Level {user1_lvl}`\n"
                                          f"`2. ♕{user2}♕ ({all_users[1][0]}) - Level {user2_lvl}`\n"
                                          f"`3. ♖{user3}♖ ({all_users[2][0]}) - Level {user3_lvl}`\n"
                                          f"`4. {user4} ({all_users[3][0]}) - Level {user4_lvl}`\n"
                                          f"`5. {user5} ({all_users[4][0]}) - Level {user5_lvl}`\n"
                                          f"`6. {user6} ({all_users[5][0]}) - Level {user6_lvl}`\n"
                                          f"`7. {user7} ({all_users[6][0]}) - Level {user7_lvl}`\n"
                                          f"`8. {user8} ({all_users[7][0]}) - Level {user8_lvl}`\n"
                                          f"`9. {user9} ({all_users[8][0]}) - Level {user9_lvl}`\n"
                                          f"`10. {user10} ({all_users[9][0]}) - Level {user10_lvl}`\n")
        endtime = int(time.time())
        embed.set_footer(text=f"Finished in {endtime - starttime}s")
        await msg.edit(embed=embed)
        
    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def ecotop(self, ctx):
        # await self.bot.get_user_info(310039170792030211)
        msg = await ctx.send(embed=discord.Embed(color=0xDEADBF, title="Top Users | Economy", description="Loading..."))
        starttime = int(time.time())
        msg
        db.execute("SELECT userid, balance FROM economy ORDER BY balance+0 DESC LIMIT 10")
        all_users = db.fetchall()
        try:
            user1 = await self.bot.get_user_info(int(all_users[0][0]))
        except:
            user1 = "Deleted User"
        user1_lvl = int(all_users[0][1])
        try:
            user2 = await self.bot.get_user_info(int(all_users[1][0]))
        except:
            user2 = "Deleted User"
        user2_lvl = int(all_users[1][1])
        try:
            user3 = await self.bot.get_user_info(int(all_users[2][0]))
        except:
            user3 = "Deleted User"
        user3_lvl = int(all_users[2][1])
        try:
            user4 = await self.bot.get_user_info(int(all_users[3][0]))
        except:
            user4 = "Deleted User"
        user4_lvl = int(all_users[3][1])
        try:
            user5 = await self.bot.get_user_info(int(all_users[4][0]))
        except:
            user5 = "Deleted User"
        user5_lvl = int(all_users[4][1])
        try:
            user6 = await self.bot.get_user_info(int(all_users[5][0]))
        except:
            user6 = "Deleted User"
        user6_lvl = int(all_users[5][1])
        try:
            user7 = await self.bot.get_user_info(int(all_users[6][0]))
        except:
            user7 = "Deleted User"
        user7_lvl = int(all_users[6][1])
        try:
            user8 = await self.bot.get_user_info(int(all_users[7][0]))
        except:
            user8 = "Deleted User"
        user8_lvl = int(all_users[7][1])
        try:
            user9 = await self.bot.get_user_info(int(all_users[8][0]))
        except:
            user9 = "Deleted User"
        user9_lvl = int(all_users[8][1])
        try:
            user10 = await self.bot.get_user_info(int(all_users[9][0]))
        except:
            user10 = "Deleted User"
        user10_lvl = int(all_users[9][1])

        embed = discord.Embed(color=0xDEADBF, title="Top Users | Economy",
                              description=f"`1. ♔{user1}♔ ({all_users[0][0]}) - ${user1_lvl}`\n"
                                          f"`2. ♕{user2}♕ ({all_users[1][0]}) - ${user2_lvl}`\n"
                                          f"`3. ♖{user3}♖ ({all_users[2][0]}) - ${user3_lvl}`\n"
                                          f"`4. {user4} ({all_users[3][0]}) - ${user4_lvl}`\n"
                                          f"`5. {user5} ({all_users[4][0]}) - ${user5_lvl}`\n"
                                          f"`6. {user6} ({all_users[5][0]}) - ${user6_lvl}`\n"
                                          f"`7. {user7} ({all_users[6][0]}) - ${user7_lvl}`\n"
                                          f"`8. {user8} ({all_users[7][0]}) - ${user8_lvl}`\n"
                                          f"`9. {user9} ({all_users[8][0]}) - ${user9_lvl}`\n"
                                          f"`10. {user10} ({all_users[9][0]}) - ${user10_lvl}`\n")
        endtime = int(time.time())
        embed.set_footer(text=f"Finished in {endtime - starttime}s")
        await msg.edit(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def transfer(self, ctx, amount : int, user : discord.Member):
        """Transfer Credits to Users"""
        if amount < 10:
            await ctx.send("Minimum send price is $10")
            return
        if user.bot:
            await ctx.send("You can't send credits to bots.")
            return
        elif user == ctx.message.author:
            await ctx.send("You cant send credits to yourself.")
            return
        else:
            if await self.usercheck('economy', ctx.message.author) is False:
                await ctx.send("You don't have a bank account...")
                return
            elif await self.usercheck('economy', user) is False:
                await ctx.send(f"{user.name} has no bank account...")
                return
            else:
                db.execute(f"SELECT balance FROM economy WHERE userid = {ctx.message.author.id}")
                author_balance = int(db.fetchone()[0])
                db.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
                user_balance = int(db.fetchone()[0])
                if (author_balance - amount) < 0:
                    await ctx.send("You don't have that much to spend.")
                    return
                else:
                    db.execute(f"UPDATE economy SET balance = {amount + user_balance} WHERE userid = {user.id}")
                    connection.commit()
                    db.execute(f"UPDATE economy SET balance = {author_balance - amount} WHERE userid = {ctx.message.author.id}")
                    connection.commit()
                    await ctx.send(f"Send `{amount}` to {user.mention}!")
                    try:
                        await user.send(f"{ctx.message.author.name} has sent you ${amount}.")
                    except:
                        pass
    #
    # async def _handle_on_message(self, message):
    #     user = message.author
    #     if user.bot:
    #         return
    #     if await self.usercheck("levels", user) is False:
    #         await self._create_user(user)
    #         return
    #     else:
    #         await asyncio.sleep(1)
    #         curr_time = time.time()
    #         db.execute(f"SELECT lastxp FROM levels WHERE userid = {user.id}")
    #         lastxp = db.fetchone()
    #         if lastxp is None:
    #             pass
    #         elif float(curr_time) - float(lastxp[0]) >= 120:
    #             await self._process_exp(user.id, random.randint(15, 20))
    #             db.execute(f"UPDATE levels SET lastxp = {time.time()} WHERE userid = {user.id}")
    #             connection.commit()
    #
    # async def _create_user(self, user):
    #     try:
    #         #userid, info, title, level, rep, lastxp,
    #         db.execute(f"INSERT INTO levels VALUES ({user.id}, info, title, 0, 0, 0, 0)")
    #         connection.commit()
    #         log.info(f"Made account for {user.name} ({user.id})")
    #     except AttributeError:
    #         pass
    #
    # async def _process_exp(self, userinfo, exp : int):
    #     await asyncio.sleep(random.randint(2, 6))
    #     db.execute("SELECT level FROM levels WHERE userid = {}".format(userinfo))
    #     levels = db.fetchone()[0]
    #     db.execute(f"UPDATE levels SET level = {levels + exp} WHERE userid = {userinfo}")
    #     connection.commit()

def setup(bot):
    n = economy(bot)
    # bot.add_listener(n._handle_on_message, "on_message")
    bot.add_cog(n)