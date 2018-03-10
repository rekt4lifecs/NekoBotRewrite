from discord.ext import commands
import discord, pymysql, config, datetime, time, aiohttp, random, asyncio, string, aiomysql
from datetime import timedelta

class Economy:
    """Economy"""

    def __init__(self, bot):
        self.bot = bot

    async def database(self, datab: str, item: str, userid: int):
        connection = await aiomysql.connect(user='root',
                                            password=config.dbpass,
                                            host='localhost',
                                            port=3306,
                                            db='nekobot')
        db = await connection.cursor()
        try:
            await db.execute(f"SELECT {item} FROM {datab} WHERE userid = {userid}")
            return await db.fetchone()[0]
        except:
            return None

    async def usercheck(self, datab: str, userid: int):
        connection = await aiomysql.connect(user='root',
                                            password=config.dbpass,
                                            host='localhost',
                                            port=3306,
                                            db='nekobot')
        db = await connection.cursor()
        if not await db.execute(f'SELECT 1 FROM {datab} WHERE userid = {userid}'):
            return False
        else:
            return True

    # @commands.command()
    # @commands.cooldown(1, 120, commands.BucketType.user)
    # async def steal(self, ctx, user : discord.Member):
    #     """Steal $$$ from some1"""
    #     connection = await aiomysql.connect(user=config.db.user,
    #                                         password=config.db.password,
    #                                         host=config.db.host,
    #                                         port=config.db.port,
    #                                         db=config.db.database)
    #     if user == ctx.message.author:
    #         await ctx.send("You can't steal from yourself 😦")
    #         return
    #     elif user.bot is True:
    #         await ctx.send("You can't steal from bots 😦")
    #         return
    #     elif await self.usercheck('economy', user.id) is False:
    #         await ctx.send("That user doesn't have an account.")
    #         return
    #     elif await self.usercheck('economy', ctx.message.author.id) is False:
    #         await ctx.send("You don't have a bank account 😦, use `register`")
    #     async with connection.cursor() as cur:
    #         await cur.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
    #         user_balance = await cur.fetchone()
    #         user_balance = int(user_balance[0])
    #         await cur.execute(f"SELECT balance FROM economy WHERE userid = {ctx.message.author.id}")
    #         author_balance = await cur.fetchone()
    #         author_balance = int(author_balance[0])
    #         if user_balance < 5000:
    #             await ctx.send("That user is too poor to steal from ;-;")
    #             return
    #         if user_balance <= 1500:
    #             await ctx.send("That user is too poor to steal from 😦")
    #             return
    #         else:
    #             x = random.randint(1, 4)
    #             stolen_amount = random.randint(1, 1500)
    #             if x == 1:
    #                 await ctx.send(f"Stolen **{stolen_amount}** from **{user.name}** successfully!")
    #                 await cur.execute(f"UPDATE economy SET balance = {user_balance - stolen_amount} WHERE userid = {user.id}")
    #                 await connection.commit()
    #                 await cur.execute(f"UPDATE economy SET balance = {author_balance + stolen_amount} WHERE userid = {ctx.message.author.id}")
    #                 await connection.commit()
    #             else:
    #                 if (author_balance - stolen_amount) < 0:
    #                     steal_bal = 0
    #                 else:
    #                     steal_bal = author_balance - stolen_amount
    #                 await ctx.send(f"Failed to steal from **{user.name}** and lost **{stolen_amount}**")
    #                 await cur.execute(f"UPDATE economy SET balance = {author_balance - steal_bal} WHERE userid = {ctx.message.author.id}")
    #                 await connection.commit()

    @commands.command()
    @commands.cooldown(1, 1200, commands.BucketType.user)
    async def work(self, ctx, seconds: int = 30):
        """Work for $$$ OwO"""
        connection = await aiomysql.connect(user='root',
                                            password=config.dbpass,
                                            host='localhost',
                                            port=3306,
                                            db='nekobot')
        author = ctx.message.author
        if await self.usercheck('economy', author.id) is False:
            await ctx.send("You don't have a bank account 😦, use `register`")
            return
        else:
            async with connection.cursor() as cur:
                await cur.execute(f"SELECT balance FROM economy WHERE userid = {author.id}")
                balance = await cur.fetchone()
                balance = int(balance[0])
                if seconds > 600:
                    seconds = 600
                elif seconds <= 0:
                    seconds = 30
                await ctx.send(f"Working for {seconds} seconds")
                await asyncio.sleep(int(seconds/2))
                try:
                    await ctx.author.send(f"{int(seconds/2)}s left to work...")
                except:
                    pass
                await asyncio.sleep(int(seconds/2))
                end_amount = int(seconds * 2.25)
                await ctx.send(f"{author.mention}, worked for {seconds} and got {end_amount} credits!")
                await cur.execute(f"UPDATE economy SET balance = {balance + end_amount} WHERE userid = {author.id}")
                await connection.commit()

    @commands.command()
    async def register(self, ctx):
        """Register a bank account."""
        user = ctx.message.author.id
        if await self.usercheck("economy", user) is False:
            connection = await aiomysql.connect(user='root',
                                                password=config.dbpass,
                                                host='localhost',
                                                port=3306,
                                                db='nekobot')
            async with connection.cursor() as cur:
                await cur.execute(f"insert into economy VALUES ({user}, 3500, 0)")
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
            connection = await aiomysql.connect(user='root',
                                                password=config.dbpass,
                                                host='localhost',
                                                port=3306,
                                                db='nekobot')
            async with connection.cursor() as cur:
                await cur.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
                balance = await cur.fetchone()
            await ctx.send("Balance: {}".format(balance[0]))
        else:
            await ctx.send("You don't have an account. Use `n!register` to make one.")

    # @commands.command()
    # async def roulette(self, ctx, amount : int = 500):
    #     """Play Roulette"""
    #     user = ctx.message.author
    #     connection = await aiomysql.connect(user='root',
    #                                         password=config.dbpass,
    #                                         host='localhost',
    #                                         port=3306,
    #                                         db='nekobot')
    #     if await self.usercheck("economy", user.id) is False:
    #         await ctx.send("You don't have a bank account. Use `n!register` to make one.")
    #     else:
    #         async with connection.cursor() as cur:
    #             await cur.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
    #             balance = await cur.fetchone()
    #             balance = int(balance[0])
    #         if (balance - amount) < 0:
    #             await ctx.send("You don't have that much to spend...")
    #         elif amount > 20000:
    #             await ctx.send("You can't spend more than 20000.")
    #         else:
    #             async with connection.cursor() as cur:
    #                 await cur.execute(f"UPDATE economy SET balance = {balance - amount} WHERE userid = {user.id}")
    #                 await connection.commit()
    #                 xx = random.randint(1, 2)
    #                 await cur.execute(f"SELECT amount FROM stats WHERE type = \"roulette_spent\"")
    #                 spent = await cur.fetchone()
    #                 spent = int(spent[0])
    #                 await cur.execute(f"UPDATE stats SET amount = {spent + amount} WHERE type = \"roulette_spent\"")
    #                 await connection.commit()
    #                 await cur.execute(f"SELECT amount FROM stats WHERE type = \"roulette_count\"")
    #                 count = await cur.fetchone()
    #                 count = int(count[0])
    #                 await cur.execute(f"UPDATE stats SET amount = {count + 1} WHERE type = \"roulette_count\"")
    #                 await connection.commit()
    #                 await cur.execute(f"SELECT amount FROM stats WHERE type = \"roulette_count\"")
    #                 count = await cur.fetchone()
    #                 count = int(count[0])
    #                 await ctx.send("Spinning...")
    #                 await asyncio.sleep(random.randint(2, 5))
    #                 if xx == 1:
    #                     lost = discord.Embed(color=0xDEADBF,
    #                                          title="You Lost",
    #                                          description=f"Previous Amount: **{balance}**\n"
    #                                                      f"New Amount: **{balance - amount}**")
    #                     lost.set_footer(text=f"Roulette Game: {count}, total spent: {spent}")
    #                     await ctx.send(embed=lost)
    #                 else:
    #                     won = discord.Embed(color=0xDEADBF,
    #                                         title="YOU WON!",
    #                                         description=f"Previews Amount: **{balance}**\n"
    #                                                     f"New Amount: **{balance + (amount * 2)}**")
    #                     won.set_footer(text=f"Roulette Game: {count}, total spent: {spent}")
    #                     await ctx.send(embed=won)
    #                     await cur.execute(f"UPDATE economy SET balance = {balance + (amount * 2)}")
    #                     await connection.commit()


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
        connection = await aiomysql.connect(user='root',
                                            password=config.dbpass,
                                            host='localhost',
                                            port=3306,
                                            db='nekobot')
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
        connection = await aiomysql.connect(user='root',
                                            password=config.dbpass,
                                            host='localhost',
                                            port=3306,
                                            db='nekobot')
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