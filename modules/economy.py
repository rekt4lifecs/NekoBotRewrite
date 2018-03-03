from discord.ext import commands
import discord, pymysql, config, datetime, time, aiohttp, random, asyncio, string, aiomysql
from datetime import timedelta

class Economy:
    """Economy"""

    def __init__(self, bot):
        self.bot = bot

    async def database(self, datab: str, item: str, userid: int):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        db = await connection.cursor()
        try:
            await db.execute(f"SELECT {item} FROM {datab} WHERE userid = {userid}")
            return await db.fetchone()[0]
        except:
            return None

    async def usercheck(self, datab: str, userid: int):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        db = await connection.cursor()
        if not await db.execute(f'SELECT 1 FROM {datab} WHERE userid = {userid}'):
            return False
        else:
            return True

    @commands.command()
    async def register(self, ctx):
        """Register a bank account."""
        user = ctx.message.author.id
        if await self.usercheck("economy", user) is False:
            connection = await aiomysql.connect(user=config.db.user,
                                                password=config.db.password,
                                                host=config.db.host,
                                                port=config.db.port,
                                                db=config.db.database)
            async with connection.cursor() as cur:
                await cur.execute(f"insert ignore into economy VALUES ({user}, 3500, 0)")
                await connection.commit()
            embed = discord.Embed(color=0xDEADBF,
                                  description="Made a bank account OwO.")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  description="You already have a bank account.")
            await ctx.send(embed=embed)

    @commands.command()
    async def balance(self, ctx, user : discord.Member = None):
        """Check your bank balance."""
        if user == None:
            user = ctx.message.author
        if await self.usercheck("economy", user.id) is not False:
            connection = await aiomysql.connect(user=config.db.user,
                                                password=config.db.password,
                                                host=config.db.host,
                                                port=config.db.port,
                                                db=config.db.database)
            async with connection.cursor() as cur:
                await cur.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
                balance = await cur.fetchone()
            await ctx.send("Balance: {}".format(balance[0]))
        else:
            await ctx.send("You don't have an account. Use `n!register` to make one.")

    # @commands.command()
    # @commands.cooldown(1, 20, commands.BucketType.user)
    # async def roulette(self, ctx, amount : int):
    #     """Play Roulette"""
    #     connection = await aiomysql.connect(user=config.db.user,
    #                                         password=config.db.password,
    #                                         host=config.db.host,
    #                                         port=config.db.port,
    #                                         db=config.db.database)
    #     if amount <= 0:
    #         await ctx.send("Amount must be higher than 0.")
    #         return
    #     user = ctx.message.author
    #     if await self.usercheck("economy", user.id) is False:
    #         await ctx.send("You don't have a bank account 😦, use `register` to make one.")
    #         return
    #     url = "https://discordbots.org/api/bots/310039170792030211/votes"
    #     async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
    #         async with cs.get(url) as r:
    #             res = await r.json()
    #     for x in res:
    #         if str(x['id']) == str(ctx.message.author.id):
    #             if amount > 25000:
    #                 await ctx.send("You can't spend more than 25000 credits.")
    #                 break
    #             eee = await self.database("economy", "balance", user.id)
    #             eco = int(eee[0])
    #             if (eco - amount) < 0:
    #                 await ctx.send("You don't have that much credits to spend ;-;")
    #                 break
    #             else:
    #                 async with connection.cursor() as cur:
    #                     await cur.execute(f"UPDATE economy SET balance = {eco - amount} WHERE userid = {user.id}")
    #                     await connection.commit()
    #                 await ctx.send("Spinning...")
    #                 await asyncio.sleep(random.randint(3, 6))
    #                 xx = random.randint(0, 1)
    #                 if xx == 0:
    #                     await ctx.send(f"You lost {amount} 😦")
    #                     break
    #                 elif xx == 1:
    #                     await ctx.send(f"YOU WON {amount * 2}!!! OwO\n"
    #                                    f"💯🔥<:flipped_ok_nko:418245464530485258>😂👌🔥💯")
    #                     async with connection.cursor() as cur:
    #                         await cur.execute(f"UPDATE economy SET balance = {eco + (amount * 2)} WHERE userid = {user.id}")
    #                         await connection.commit()
    #                     break
    #     else:
    #         if amount > 5000:
    #             await ctx.send(embed=discord.Embed(color=0xDEADBF,
    #                                                url="https://discordbots.org/bot/310039170792030211/vote",
    #                                                title="Vote",
    #                                                description="to get access to spend up to 25k at once OwO"))
    #             return
    #         eee = await self.database("economy", "balance", user.id)
    #         eco = int(eee[0])
    #         if (eco - amount) < 0:
    #             await ctx.send("You don't have that much credits to spend ;-;")
    #             return
    #         async with connection.cursor() as cur:
    #             await cur.execute(f"UPDATE economy SET balance = {eco - amount} WHERE userid = {user.id}")
    #             await connection.commit()
    #         await ctx.send("Spinning...")
    #         await asyncio.sleep(random.randint(3, 6))
    #         xx = random.randint(0, 1)
    #         if xx == 0:
    #             await ctx.send(f"You lost {amount} 😦")
    #         elif xx == 1:
    #             await ctx.send(f"YOU WON {amount * 2}!!! OwO\n"
    #                            f"💯🔥<:flipped_ok_nko:418245464530485258>😂👌🔥💯")
    #             async with connection.cursor() as cur:
    #                 await cur.execute(f"UPDATE economy SET balance = {eco + (amount * 2)} WHERE userid = {user.id}")
    #                 await connection.commit()
    #
    @commands.command()
    async def transfer(self, ctx, user : discord.Member, amount : int):
        """Transfer Credits to a User"""
        author = ctx.message.author
        if user == author:
            await ctx.send("You can't send money to yourself.")
            return
        if amount <= 0:
            await ctx.send("Transfer amount can't be 0 or under 0.")
            return
        if await self.usercheck("economy", ctx.message.author.id) is False:
            await ctx.send("You don't have a bank account 😦, use `register` to make one.")
            return
        elif await self.usercheck("economy", user.id) is False:
            await ctx.send(f"The user you are sending credits too doesn't have a bank account 😦")
            return
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        async with connection.cursor() as cur:
            await cur.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
            user_account = await cur.fetchone()
            user_account = int(user_account[0])
            await cur.execute(f"SELECT balance FROM economy WHERE userid = {author.id}")
            author_account = await cur.fetchone()
            author_account = int(author_account[0])
        if (int(author_account) - amount) < 0:
            await ctx.send("You don't have that amount of credit to send...")
            return
        async with connection.cursor() as cur:
            await cur.execute(f"UPDATE economy SET balance = {author_account - amount} WHERE userid = {author.id}")
            await connection.commit()
            await cur.execute(f"UPDATE economy SET balance = {user_account + amount} WHERE userid = {user.id}")
            await connection.commit()
        pin = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        embed = discord.Embed(color=0xDEADBF,
                              title="Transfer Confirmation",
                              description=f"RECEIPT: **{pin}**\n"
                                          f"TO: **{user.name}**\n"
                                          f"FROM: **{author.name}**\n"
                                          f"AMOUNT: **{amount}**")
        await ctx.send(embed=embed)

    @commands.command(aliases=["payday"])
    async def daily(self, ctx):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        user = ctx.message.author
        if await self.usercheck("economy", user.id) is False:
            await ctx.send("You don't have a bank account 😦, use `register` to make one.")
            return
        else:
            async with connection.cursor() as cur:
                await cur.execute(f"SELECT payday FROM economy WHERE userid = {user.id}")
                getdb = await cur.fetchone()
            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(int(getdb[0])).strftime("%d")
            if timecheck == timenow:
                tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1),
                                                     hour=0, minute=0, second=0)
                delta = tomorrow - datetime.datetime.now()
                timeleft = time.strftime("%H", time.gmtime(delta.seconds))
                await ctx.send(f"Wait another {timeleft} hours before using daily again...")
                return
            async with connection.cursor() as cur:
                await cur.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
                eco = await cur.fetchone()
            eco = int(eco[0])

            # Voters X3 Payday #############################
            url = "https://discordbots.org/api/bots/310039170792030211/votes"
            async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
                async with cs.get(url) as r:
                    res = await r.json()
            for x in res:
                if str(x['id']) == str(ctx.message.author.id):
                    async with connection.cursor() as cur:
                        await cur.execute(f"UPDATE economy SET balance = {eco + 7500} WHERE userid = {user.id}")
                        await connection.commit()
                        await cur.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}")
                        await connection.commit()
                    embed = discord.Embed(color=0xDEADBF,
                                          title="Daily Credits",
                                          description="Recieved 2500 + 5000 Daily credits - Voter Bonus!")
                    await ctx.send(embed=embed)
                    break
            #################################################
            else:
                async with connection.cursor() as cur:
                    await cur.execute(f"UPDATE economy SET balance = {eco + 2500} WHERE userid = {user.id}")
                    await connection.commit()
                    await cur.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}")
                    await connection.commit()
                embed = discord.Embed(color=0xDEADBF,
                                      title="Daily Credits",
                                      description="Recieved 2500 Daily credits!")
                embed.set_footer(text="Pssst voting will give you 3 times the daily bonus OwO, vote with .vote")
                await ctx.send("Received 2500 credits!")


def setup(bot):
    bot.add_cog(Economy(bot))