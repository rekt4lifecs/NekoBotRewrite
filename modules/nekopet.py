from discord.ext import commands
import discord, random, math, logging
from PIL import Image, ImageFont, ImageDraw
import rethinkdb as r
from io import BytesIO
import gettext

log = logging.getLogger()

class NekoPet:

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("nekopet", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

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
            _ = await self._get_text(ctx)
            return await ctx.send(_("Neko Pet OwO\n\n"
                                  "**n!pet play** - Play with your neko\n"
                                  "**n!pet show** - Show your pet\n"
                                  "**n!pet shop** - Shop for a neko or buy items for it\n"
                                  "**n!pet feed** - Feed your neko\n"
                                  "**n!pet train** - Train your neko to learn new tricks."))

    @pet.command(name="play")
    async def neko_play(self, ctx):
        """Play with your neko!"""
        _ = await self._get_text(ctx)
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send(_("You don't have a pet to play with ;c, buy one with `n!pet shop`"))
        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
        play = pet_data["play"]
        if play >= 90:
            return await ctx.send(_("**Your neko is too tired to play.**"))
        if random.randint(1, 2) == 1:
            am = random.randint(10, 30)
            newplay = play + am
            if newplay >= 100:
                newplay = 100
            await r.table("nekopet").get(str(ctx.author.id)).update({"play": newplay}).run(self.bot.r_conn)
            await ctx.send(_("<a:rainbowNekoDance:462373594555613214> | **Your neko is now happy :3 (%s attention)**") % am)
        else:
            await ctx.send(_("**Your neko doesn't feel like playing, maybe try again later.**"))

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
        _ = await self._get_text(ctx)
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send("❌ | " + _("You don't have a pet to play with ;c, buy one with `n!pet shop`"))

        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)

        level = pet_data["level"]
        food = pet_data["food"]
        play = pet_data["play"]
        type = pet_data["type"]

        data_folder = "data/nekopet/"
        background = Image.open(data_folder + pet_data.get("background", "background.png")).convert("RGBA")
        font = ImageFont.truetype("data/fonts/Neko.ttf", 30)

        types = {
            1: "neko1.png",
            2: "neko2.png",
            3: "neko3.png",
            4: "neko4.png"
        }

        draw = ImageDraw.Draw(background)
        neko = Image.open(data_folder + types[int(type)]).resize((250, background.size[1])).convert("RGBA")

        background.alpha_composite(neko)
        draw.text((225, 5), f"{food}% Food", (255, 255, 255), font)
        draw.text((225, 45), f"{play}% Play", (255, 255, 255), font)
        draw.text((225, 85), f"Level {self._find_level(int(level))}", (255, 255, 255), font)

        temp = BytesIO()
        background.save(temp, format="png")
        temp.seek(0)

        em = discord.Embed(color=0xDEADBF, title=f"{ctx.message.author.name}'s " + "neko" if not int(type) == 4 else "86")
        em.set_footer(text=f"Level: {self._find_level(int(level))}, XP: {level}")
        await ctx.send(file=discord.File(fp=temp, filename="neko.png"),
                       embed=em.set_image(url=f"attachment://neko.png"))

    def get_neko_type(self):
        if random.randint(1, 500) == 1:
            return 4
        else:
            return random.randint(1, 3)

    @pet.command(name="shop")
    async def neko_shop(self, ctx):
        """Shop for a neko or buy items for it!"""
        _ = await self._get_text(ctx)
        if not await self.__has_bank(ctx.author.id):
            return await ctx.send("❌ | " + _("**You dont have a bank account, how will you buy anything?!**"))

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author

        em = discord.Embed(color=0xDEADBF, title=_("Neko Shop"),
                           description=_("1 = Buy a Neko ($75,000)\n2 = Buy backgrounds")).set_footer(text=_("More coming soon..."))
        em.set_footer(text=_("Type a number."))
        strt = await ctx.send(embed=em)

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=15.0)
        except:
            return await strt.edit(content=_("**Timed out...**"), embed=None)
        try:
            content = int(msg.content)
        except:
            return await ctx.send("❌ | " + _("Invalid option, returning..."))

        if content == 1:
            if await self.__check_pet(ctx.author.id):
                await strt.edit(content=_("**You already have a neko, would you like to replace it?** (Type `yes` if you would like to.)"),
                                       embed=None)
            else:
                await strt.edit(content=_("**Are you sure you want to buy a neko?** (Type `yes` if you would like to.)"),
                                       embed=None)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            except:
                return await strt.edit(content="❌ | **Timed out...**", embed=None)
            if msg.content.lower() == "yes":
                if not await self.__can_purchase(ctx.author.id, 75000):
                    return await strt.edit(content="❌ | " + _("**You don't have enough $ ;c**"))
                await self.__remove_amount(ctx.author.id, 75000)
                data = {
                    "id": str(ctx.author.id),
                    "background": "background.png",
                    "level": 0,
                    "type": self.get_neko_type(),
                    "food": 100,
                    "play": 100
                }
                await r.table("nekopet").get(str(ctx.author.id)).delete().run(self.bot.r_conn)
                await r.table("nekopet").insert(data).run(self.bot.r_conn)
                log.info("%s (%s) bought a neko." % (ctx.author.name, ctx.author.id,))
                return await strt.edit(content=_("<a:rainbowNekoDance:462373594555613214> | Successfully bought a neko!"))
            else:
                return await strt.edit(content=_("❌ | Returned..."))
        elif content == 2:
            if not await self.__check_pet(ctx.author.id):
                return await strt.edit(embed=None, content="❌ | " + _("You don't have a pet to buy a background for"))
            em = discord.Embed(color=0xDEADBF)
            em.title = _("Backgrounds")
            em.description = _("1 = Default (Free)\n" \
                               "2 = Cubes ($250,000)")
            await strt.edit(embed=em)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            except:
                return await strt.edit(content="❌ | " + _("**Timed out...**"), embed=None)
            try:
                msg = int(msg.content)
            except:
                return await strt.edit(content="❌ | " + _("Invalid option, returning..."))
            user_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
            if msg == 1:
                if user_data.get("background", "background.png") == "background.png":
                    return await strt.edit(content="❌ | " + _("**You already have this background active**"), embed=None)
                await ctx.send(_("Are you sure you want to reset your background? (Type `yes` if you would like to.)"))
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                except:
                    return await strt.edit(content="❌ | **Timed out...**", embed=None)
                if msg.content.lower() == "yes":
                    await r.table("nekopet").get(str(ctx.author.id)).update({"background": "background.png"}).run(self.bot.r_conn)
                    return await ctx.send(_("<a:rainbowNekoDance:462373594555613214> | Successfully reset your background!"))
                else:
                    return await strt.edit(content="❌ | " + _("Returned..."))
            elif msg == 2:
                if user_data.get("background", "background.png") == "background2.png":
                    return await strt.edit(content="❌ | " + _("**You already have this background active**"), embed=None)
                em = discord.Embed(color=0x7243DB)
                await ctx.send(content=_("**Are you sure you want to buy a background?** (Type `yes` if you would like to.)"),
                               file=discord.File("data/nekopet/background2.png", filename="nekobackground.png"),
                               embed=em.set_image(url="attachment://nekobackground.png"))
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                except:
                    return await strt.edit(content="❌ | " + _("**Timed out...**"), embed=None)
                if msg.content.lower() == "yes":
                    if not await self.__can_purchase(ctx.author.id, 250000):
                        return await ctx.send(content="❌ | " + _("**You don't have enough $ ;c**"), embed=None)
                    else:
                        await self.__remove_amount(ctx.author.id, 250000)
                        await r.table("nekopet").get(str(ctx.author.id)).update({"background": "background2.png"}).run(self.bot.r_conn)
                        return await ctx.send(_("<a:rainbowNekoDance:462373594555613214> | Successfully bought the background!"))
                else:
                    return await ctx.send(content="❌ | " + _("Returned..."))
            else:
                return await ctx.send("❌ | " + _("Invalid option, returning..."))
        else:
            return await ctx.send("❌ | " + _("Invalid option, returning..."))

    @pet.command(name="feed")
    async def neko_feed(self, ctx):
        """Feed your neko"""
        _ = await self._get_text(ctx)
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send("❌ | " + _("You don't have a pet to play with ;c, buy one with `n!pet shop`"))
        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
        food = pet_data["food"]
        if food >= 90:
            return await ctx.send("❌ | " + _("**Your neko already has enough food!**"))
        payamount = random.randint(250, 5000)
        if not await self.__can_purchase(ctx.author.id, payamount):
            return await ctx.send("❌ | " + ("**You don't have enough money for food ;c*"))
        try:
            await self.__remove_amount(ctx.author.id, payamount)
            await r.table("nekopet").get(str(ctx.author.id)).update({"food": 100}).run(self.bot.r_conn)
            await ctx.send(_("<a:rainbowNekoDance:462373594555613214> | **Paid %s for your nekos food!**") % payamount)
        except Exception as e:
            await ctx.send("❌ | " + _("**Failed to remove balance. `%s`") % e)

    @pet.command(name="train")
    async def neko_train(self, ctx):
        _ = await self._get_text(ctx)
        if not await self.__check_pet(ctx.author.id):
            return await ctx.send(_("You don't have a pet to play with ;c, buy one with `n!pet shop`"))
        pet_data = await r.table("nekopet").get(str(ctx.author.id)).run(self.bot.r_conn)
        level = pet_data["level"]
        if random.randint(1, 4) == 1:
            am = random.randint(10, 100)
            newlvl = level + am
            await r.table("nekopet").get(str(ctx.author.id)).update({"level": newlvl}).run(self.bot.r_conn)
            await ctx.send(_("**Your neko learnt new tricks owo (%s score)**") % am)
        else:
            await ctx.send(_("**Your neko doesn't feel like playing, maybe try again later.**"))

def setup(bot):
    bot.add_cog(NekoPet(bot))