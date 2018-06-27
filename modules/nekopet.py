from discord.ext import commands
import discord, random, os, math, logging
from PIL import Image, ImageFont, ImageDraw

log = logging.getLogger()

#
# Formatting
# UserID | Name | Level | Type | Food | Play
#

class NekoPet:

    def __init__(self, bot):
        self.bot = bot

    async def check(self, user:int):
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if await db.execute(f"SELECT 1 FROM nekopet WHERE userid = {user}"):
                    return True
                else:
                    return False

    async def bal_check(self, user:int, amount:int):
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                bal = await db.execute(f"SELECT balance FROM economy WHERE userid = {user}")
                if bal:
                    bal = await db.fetchone()
                    bal = int(bal[0])
                    if bal <= amount:
                        return False
                    else:
                        return True
                else:
                    return False

    async def create(self, user: int, name:str=None, type:int=None, update:bool=False):
        if type is None:
            type = random.randint(1, 3)
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if update:
                    await db.execute(f"UPDATE nekopet SET food = 100 WHERE userid = {user}")
                    await db.execute(f"UPDATE nekopet SET play = 100 WHERE userid = {user}")
                    await db.execute(f"UPDATE nekopet SET type = {type} WHERE userid = {user}")
                    await db.execute(f"UPDATE nekopet SET level = 0 WHERE userid = {user}")
                else:
                    await db.execute(f"INSERT INTO nekopet VALUES ({user}, \"neko\", 0, {type}, 100, 100)")

    async def remove_balance(self, user:int, amount:int):
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(f"SELECT balance FROM economy WHERE userid = {user}")
                balance = await db.fetchone()
                balance = int(balance[0])
                newbal = balance - amount
                await db.execute(f"UPDATE economy SET balance = {int(newbal)} WHERE userid = {user}")

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

    async def has_bank(self, user:int):
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if await db.execute(f"SELECT 1 FROM economy WHERE userid = {user}"):
                    return True
                else:
                    return False

    @commands.group()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pet(self, ctx):
        """Neko pet owo"""
        if ctx.invoked_subcommand is None:
            return await ctx.send("Neko Pet OwO\n\n"
                                  "**n!pet play** - Play with your neko\n"
                                  "**n!pet show** - Show your pet\n"
                                  "**n!pet shop** - Shop for a neko or buy items for it\n"
                                  "**n!pet feed** - Feed your neko\n"
                                  "**n!pet train** - Train your neko to learn new tricks.")

    @pet.command(name="play")
    async def neko_play(self, ctx):
        """Play with your neko!"""
        if not await self.check(ctx.message.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")
        play = await self.execute(f"SELECT play FROM nekopet WHERE userid = {ctx.message.author.id}", isSelect=True)
        play = int(play[0])
        if play >= 90:
            return await ctx.send("**Your neko is too tired to play.**")
        if random.randint(1, 2) == 1:
            am = random.randint(10, 30)
            newplay = play + am
            if newplay >= 100:
                newplay = 100
            await self.execute(f"UPDATE nekopet SET play = {newplay} WHERE userid = {ctx.message.author.id}", commit=True)
            await ctx.send(f"**Your neko is now happy :3 ({am} attention)**")
        else:
            await ctx.send("**Your neko doesn't feel like playing, maybe try again later.**")

    def _required_exp(self, level: int):
        if level < 0:
            return 0
        return 139 * level + 65

    def _level_exp(self, level: int):
        return level * 65 + 139 * level * (level - 1) // 2

    def _find_level(self, total_exp):
        return int((1 / 278) * (9 + math.sqrt(81 + 1112 * (total_exp))))

    @pet.command(name="show")
    async def neko_show(self, ctx):
        """Show your pet"""
        await ctx.trigger_typing()
        if not await self.check(ctx.message.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")
        items = await self.execute(f"SELECT level, food, play, type FROM nekopet WHERE userid = {ctx.message.author.id}",
                                   isSelect=True)
        userpath = f"data/nekopet/{ctx.message.author.id}.png"

        if os.path.exists(userpath):
            os.remove(userpath)

        level = items[0]
        food = items[1]
        play = items[2]
        type = items[3]

        data_folder = "data/nekopet/"
        background = Image.open(data_folder + "background.png").convert("RGBA")
        font = ImageFont.truetype("data/fonts/Neko.ttf", 30)

        if int(type) == 1:
            neko = data_folder + "neko1.png"
        elif int(type) == 2:
            neko = data_folder + "neko2.png"
        elif int(type) == 3:
            neko = data_folder + "neko3.png"
        else:
            neko = None

        draw = ImageDraw.Draw(background)
        neko = Image.open(neko).resize((250, background.size[1]))

        background.alpha_composite(neko)
        draw.text((225, 5), f"{food}% Food", (255, 255, 255), font)
        draw.text((225, 45), f"{play}% Play", (255, 255, 255), font)
        draw.text((225, 85), f"Level {self._find_level(int(level))}", (255, 255, 255), font)

        background.save(userpath)

        em = discord.Embed(color=0xDEADBF, title=f"{ctx.message.author.name}'s Neko")
        em.set_footer(text=f"Level: {self._find_level(int(level))}, XP: {level}")
        await ctx.send(file=discord.File(userpath),
                       embed=em.set_image(url=f"attachment://{ctx.message.author.id}.png"))

    @pet.command(name="shop")
    async def neko_shop(self, ctx):
        """Shop for a neko or buy items for it!"""
        if not await self.has_bank(ctx.message.author.id):
            return await ctx.send("**You dont have a bank account, how will you buy anything?!**")
        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author
        em = discord.Embed(color=0xDEADBF, title="Neko Shop",
                           description="1 = Buy a Neko ($50,000)").set_footer(text="More coming soon...")
        em.set_footer(text="Type a number.")
        strt = await ctx.send(embed=em)
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=15.0)
        except:
            return await strt.edit(content="**Timed out...**", embed=None)
        try:
            content = int(msg.content)
        except:
            return await ctx.send("Invalid option, returning...")
        if content == 1:
            if await self.check(ctx.message.author.id):
                await strt.edit(content="**You already have a neko, would you like to replace it?** (Type `yes` if you would like to.)",
                                       embed=None)
                owned = True
            else:
                await strt.edit(content="**Are you sure you want to buy a neko?** (Type `yes` if you would like to.)",
                                       embed=None)
                owned = False
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            except:
                return await strt.edit(content="**Timed out...**", embed=None)
            if msg.content.lower() == "yes":
                if not await self.bal_check(ctx.message.author.id, 50000):
                    return await strt.edit(content="**You don't have enough $ ;c**")
                await self.remove_balance(ctx.message.author.id, 50000)
                await self.create(ctx.message.author.id, name=f"{ctx.message.author.name}'s Neko", update=owned)
                return await strt.edit(content="Successfully bought a neko!")
            else:
                return await strt.edit(content="Returned...")
        else:
            return await ctx.send("Invalid option, returning...")

    @pet.command(name="feed")
    async def neko_feed(self, ctx):
        """Feed your neko"""
        if not await self.check(ctx.message.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")
        food = await self.execute(f"SELECT food FROM nekopet WHERE userid = {ctx.message.author.id}", isSelect=True)
        food = int(food[0])
        if food >= 90:
            return await ctx.send("**Your neko already has enough food!**")
        payamount = random.randint(250, 3000)
        if not await self.bal_check(ctx.message.author.id, payamount):
            return await ctx.send("**You don't have enough food to give your pet ;c*")
        try:
            await self.remove_balance(ctx.message.author.id, payamount)
            await self.execute(f"UPDATE nekopet SET food = 100 WHERE userid = {ctx.message.author.id}", commit=True)
            await ctx.send(f"**Paid {payamount} for your nekos food!**")
        except Exception as e:
            await ctx.send(f"**Failed to remove balance. `{e}`")

    @pet.command(name="train")
    async def neko_train(self, ctx):
        if not await self.check(ctx.message.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")
        level = await self.execute(f"SELECT level FROM nekopet WHERE userid = {ctx.message.author.id}", isSelect=True)
        level = int(level[0])
        if random.randint(1, 5) == 1:
            am = random.randint(10, 30)
            newlvl = level + am
            await self.execute(f"UPDATE nekopet SET level = {newlvl} WHERE userid = {ctx.message.author.id}",
                               commit=True)
            await ctx.send(f"**Your neko learnt new tricks owo ({am} score)**")
        else:
            await ctx.send("**Your neko doesn't feel like playing, maybe try again later.**")

    async def on_message(self, message):
        if message.author.bot:
            return
        if random.randint(1, 125) == 1:
            if await self.check(message.author.id):
                data = await self.execute(f"SELECT food, play FROM nekopet WHERE userid = {message.author.id}",
                                          isSelect=True)
                if data[1] <= 0:
                    await self.execute(f"UPDATE nekopet SET play = 0 WHERE userid = {message.author.id}")
                await self.execute(f"UPDATE nekopet SET food = {int(data[0]) - random.randint(1, 20)} WHERE userid = {message.author.id}")
                await self.execute(f"UPDATE nekopet SET play = {int(data[1]) - random.randint(1, 20)} WHERE userid = {message.author.id}")
                if data[0] <= 0:
                    await self.execute(f"DELETE FROM nekopet WHERE userid = {message.author.id}")
                    log.info(f"{message.author.name} Neko Died.")

def setup(bot):
    bot.add_cog(NekoPet(bot))