from discord.ext import commands
import discord, pymysql, config, datetime, time

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

    def _get_balance(self, user):
        db.execute("SELECT balance FROM economy WHERE userid = {}".format(user.id))
        return db.fetchone()[0]

    def _has_account(self, user):
        if db.execute('SELECT 1 FROM economy WHERE userid = {}'.format(user.id)):
            return True
        else:
            return False

    def _deposit(self, user, amount : int):
        if amount <= 0:
            return
        db.execute(f"UPDATE economy SET balance = {self._get_balance(user) + amount} WHERE userid = {user.id}")
        connection.commit()

    def _withdraw(self, user, amount : int):
        if amount <= 0:
            return
        elif (self._get_balance(user) - amount) <= 0:
            return
        db.execute(f"UPDATE economy SET balance = {self._get_balance(user) - amount} WHERE userid = {user.id}")
        connection.commit()

    @commands.command()
    async def register(self, ctx):
        """Register a bank account."""
        user = ctx.message.author.id
        if not self._has_account(user):
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
        if self._has_account(user):
            await ctx.send("Balance: {}".format(self._get_balance(user)))

    @commands.command(aliases=["payday"])
    async def daily(self, ctx):
        user = ctx.message.author
        if self._has_account(user):
            db.execute(f"SELECT payday FROM economy WHERE userid = {user.id}")
            getdb = db.fetchone()[0]
            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(int(getdb)).strftime("%d")
            if timecheck == timenow:
                await ctx.send("Wait another day before using daily again...")
                return
            self._deposit(user, 2500)
            db.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}")
            connection.commit()
            await ctx.send(f"Received 2500 credits! {self._get_balance(user)} total!")
        else:
            await ctx.send("You don't have a bank account 😦, use `register` to make one.")

def setup(bot):
    bot.add_cog(Economy(bot))