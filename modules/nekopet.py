from discord.ext import commands
import discord, random, os, math, logging
from PIL import Image, ImageFont, ImageDraw
import rethinkdb as r

log = logging.getLogger()

#
# Formatting
# UserID | Name | Level | Type | Food | Play
#

class NekoPet:

    def __init__(self, bot):
        self.bot = bot

    async def __check_pet(self, user:int):
        if await r.table("nekopet").get(str(user)).run(self.bot.r_conn):
            return True
        else:
            return False

    async def __has_bank(self, user:int):
        if await r.table("economy").get(str(user)).run(self.bot.r_conn):
            return True
        else:
            return False

    async def __can_purchase(self, user:int, amount:int):
        data = await r.table("economy").get(str(user)).run(self.bot.r_conn)
        balance = data["balance"]
        if (balance - amount) < 0:
            return False
        else:
            return True

    async def __remove_amount(self, user:int, amount:int):
        data = await r.table("economy").get(str(user)).run(self.bot.r_conn)
        balance = data["balance"]
        await r.table("economy").get(str(user)).update({"balance": balance - amount}).run(self.bot.r_conn)

    @commands.group()
    @commands.guild_only()
    @commands.cooldown(1, 7, commands.BucketType.user)
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
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")
        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
        play = pet_data["play"]
        if play >= 90:
            return await ctx.send("**Your neko is too tired to play.**")
        if random.randint(1, 2) == 1:
            am = random.randint(10, 30)
            newplay = play + am
            if newplay >= 100:
                newplay = 100
            await r.table("nekopet").get(str(ctx.author.id)).update({"play": newplay}).run(self.bot.r_conn)
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
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")

        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
        userpath = f"data/nekopet/{ctx.author.id}.png"

        if os.path.exists(userpath):
            os.remove(userpath)

        level = pet_data["level"]
        food = pet_data["food"]
        play = pet_data["play"]
        type = pet_data["type"]

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
        if not await self.__has_bank(ctx.author.id):
            return await ctx.send("**You dont have a bank account, how will you buy anything?!**")

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author

        em = discord.Embed(color=0xDEADBF, title="Neko Shop",
                           description="1 = Buy a Neko ($75,000)").set_footer(text="More coming soon...")
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
            if await self.__check_pet(ctx.author.id):
                await strt.edit(content="**You already have a neko, would you like to replace it?** (Type `yes` if you would like to.)",
                                       embed=None)
            else:
                await strt.edit(content="**Are you sure you want to buy a neko?** (Type `yes` if you would like to.)",
                                       embed=None)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            except:
                return await strt.edit(content="**Timed out...**", embed=None)
            if msg.content.lower() == "yes":
                if not await self.__can_purchase(ctx.author.id, 75000):
                    return await strt.edit(content="**You don't have enough $ ;c**")
                await self.__remove_amount(ctx.author.id, 75000)
                data = {
                    "id": str(ctx.author.id),
                    "level": 0,
                    "type": random.randint(1, 3),
                    "food": 100,
                    "play": 100
                }
                await r.table("nekopet").get(str(ctx.author.id)).delete().run(self.bot.r_conn)
                await r.table("nekopet").insert(data).run(self.bot.r_conn)
                log.info("%s (%s) bought a neko." % (ctx.author.name, ctx.author.id,))
                return await strt.edit(content="Successfully bought a neko!")
            else:
                return await strt.edit(content="Returned...")
        else:
            return await ctx.send("Invalid option, returning...")

    @pet.command(name="feed")
    async def neko_feed(self, ctx):
        """Feed your neko"""
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")
        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
        food = pet_data["food"]
        if food >= 90:
            return await ctx.send("**Your neko already has enough food!**")
        payamount = random.randint(250, 5000)
        if not await self.__can_purchase(ctx.author.id, payamount):
            return await ctx.send("**You don't have enough money for food ;c*")
        try:
            await self.__remove_amount(ctx.author.id, payamount)
            await r.table("nekopet").get(str(ctx.author.id)).update({"food": 100}).run(self.bot.r_conn)
            await ctx.send(f"**Paid {payamount} for your nekos food!**")
        except Exception as e:
            await ctx.send(f"**Failed to remove balance. `{e}`")

    @pet.command(name="train")
    async def neko_train(self, ctx):
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send("You don't have a pet to play with ;c, buy one with `n!pet shop`")
        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
        level = pet_data["level"]
        if random.randint(1, 4) == 1:
            am = random.randint(10, 100)
            newlvl = level + am
            await r.table("nekopet").get(str(ctx.author.id)).update({"level": newlvl}).run(self.bot.r_conn)
            await ctx.send(f"**Your neko learnt new tricks owo ({am} score)**")
        else:
            await ctx.send("**Your neko doesn't feel like playing, maybe try again later.**")

    async def on_message(self, message):
        if message.author.bot:
            return
        if random.randint(1, 125) == 1:
            if await self.__check_pet(message.author.id):
                data = await r.table("nekopet").get(str(message.author.id)).run(self.bot.r_conn)
                if data["play"] <= 0:
                    await r.table("nekopet").get(str(message.author.id)).delete().run(self.bot.r_conn)
                else:
                    await r.table("nekopet").get(str(message.author.id)).update({"play": data["play"] - random.randint(1, 20)}).run(self.bot.r_conn)
                await r.table("nekopet").get(str(message.author.id)).update({"food": data["food"] - random.randint(1, 20)}).run(self.bot.r_conn)
                if data["food"] <= 0:
                    await r.table("nekopet").get(str(message.author.id)).delete().run(self.bot.r_conn)
                    log.info(f"{message.author.name} Neko Died.")

def setup(bot):
    bot.add_cog(NekoPet(bot))