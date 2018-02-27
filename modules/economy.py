from discord.ext import commands
import discord, pymysql, config, datetime, time, aiohttp, random, asyncio

connection = pymysql.connect(user=config.db.user,
                             password=config.db.password,
                             host=config.db.host,
                             port=config.db.port,
                             database=config.db.database)
db = connection.cursor()

class Economy:
    """Economy"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx):
        """Register a bank account."""
        db.execute("SELECT * FROM economy")
        user = ctx.message.author.id
        if not db.execute('select 1 from economy where userid = {}'.format(user)):
            db.execute(f"insert ignore into economy VALUES ({user}, 3500, 0)")
            connection.commit()
            embed = discord.Embed(color=0xDEADBF,
                                  description="Made a bank account OwO.")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  description="You already have a bank account.")
            await ctx.send(embed=embed)

    @commands.command()
    async def balance(self, ctx):
        """Check your bank balance."""
        user = ctx.message.author
        if db.execute('select 1 from economy where userid = {}'.format(user.id)):
            db.execute("select balance from economy where userid = {}".format(user.id))
            await ctx.send("Balance: {}".format(db.fetchone()[0]))
        else:
            await ctx.send("You don't have a bank account 😦, use `register` to make one.")

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def roulette(self, ctx, amount : int):
        """Play Roulette"""
        user = ctx.message.author
        if not db.execute('SELECT 1 FROM economy WHERE userid = {}'.format(user.id)):
            await ctx.send("You don't have a bank account 😦, use `register` to make one.")
            return
        url = "https://discordbots.org/api/bots/310039170792030211/votes"
        async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
            async with cs.get(url) as r:
                res = await r.json()
        for x in res:
            if str(x['id']) == str(ctx.message.author.id):
                if amount > 25000:
                    await ctx.send("You can't spend more than 25000 credits.")
                    break
                db.execute("select balance from economy where userid = {}".format(user.id))
                eco = int(db.fetchone()[0])
                if (eco - amount) < 0:
                    await ctx.send("You don't have that much credits to spend ;-;")
                    break
                else:
                    db.execute(f"UPDATE economy SET balance = {eco - amount} WHERE userid = {user.id}")
                    connection.commit()
                    await ctx.send("Spinning...")
                    await asyncio.sleep(random.randint(3, 6))
                    xx = random.randint(0, 1)
                    if xx == 0:
                        await ctx.send(f"You lost {amount} 😦")
                        break
                    elif xx == 1:
                        await ctx.send(f"YOU WON {amount * 2}!!! OwO")
                        db.execute(f"UPDATE economy SET balance = {eco + (amount * 2)} WHERE userid = {user.id}")
                        connection.commit()
                        break
        else:
            if amount > 5000:
                await ctx.send(embed=discord.Embed(color=0xDEADBF,
                                                   url="https://discordbots.org/bot/310039170792030211/vote",
                                                   title="Vote",
                                                   description="to get access to spend up to 25k at once OwO"))
                return
            db.execute("select balance from economy where userid = {}".format(user.id))
            eco = int(db.fetchone()[0])
            if (eco - amount) < 0:
                await ctx.send("You don't have that much credits to spend ;-;")
                return
            db.execute(f"UPDATE economy SET balance = {eco - amount} WHERE userid = {user.id}")
            connection.commit()
            await ctx.send("Spinning...")
            await asyncio.sleep(random.randint(3, 6))
            xx = random.randint(0, 1)
            if xx == 0:
                await ctx.send(f"You lost {amount} 😦")
            elif xx == 1:
                await ctx.send(f"YOU WON {amount * 2}!!! OwO")
                db.execute(f"UPDATE economy SET balance = {eco + (amount * 2)} WHERE userid = {user.id}")
                connection.commit()

    @commands.command(aliases=["payday"])
    async def daily(self, ctx):
        user = ctx.message.author
        if not db.execute('select 1 from economy where userid = {}'.format(user.id)):
            await ctx.send("You don't have a bank account 😦, use `register` to make one.")
            return
        else:
            db.execute(f"SELECT payday FROM economy WHERE userid = {user.id}")
            getdb = db.fetchone()[0]
            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(int(getdb)).strftime("%d")
            if timecheck == timenow:
                await ctx.send("Wait another day before using daily again...")
                return
            db.execute("select balance from economy where userid = {}".format(user.id))
            eco = int(db.fetchone()[0])

            # Voters X3 Payday #############################
            url = "https://discordbots.org/api/bots/310039170792030211/votes"
            async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
                async with cs.get(url) as r:
                    res = await r.json()
            for x in res:
                if str(x['id']) == str(ctx.message.author.id):
                    db.execute(f"UPDATE economy SET balance = {eco + 7500} WHERE userid = {user.id}")
                    connection.commit()
                    db.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}")
                    connection.commit()
                    embed = discord.Embed(color=0xDEADBF,
                                          title="Daily Credits",
                                          description="Recieved 2500 + 5000 Daily credits + Voter Bonus!")
                    await ctx.send(embed=embed)
                    break
            #################################################
            else:
                db.execute(f"UPDATE economy SET balance = {eco + 2500} WHERE userid = {user.id}")
                connection.commit()
                db.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}")
                connection.commit()
                embed = discord.Embed(color=0xDEADBF,
                                      title="Daily Credits",
                                      description="Recieved 2500 Daily credits!")
                embed.set_footer(text="Pssst voting will give you 3 times the daily bonus OwO, vote with .vote")
                await ctx.send("Received 2500 credits!")


def setup(bot):
    bot.add_cog(Economy(bot))