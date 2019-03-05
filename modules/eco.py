import rethinkdb as r
from discord.ext import commands
import discord
from config import weeb
import aiohttp, asyncio
import base64, random
import datetime, time, math
from prettytable import PrettyTable
import gettext

import cv2
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO

auth = {"Authorization": "Wolke " + weeb,
        "User-Agent": "NekoBot/4.2.0"}

def interpolate(f_co, t_co, interval):
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]

def get_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

__cjk = [
    {"from": ord(u"\u4E00"), "to": ord(u"\u9fff")},
    {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
    {"from": ord(u"\U00020000"), "to": ord(u"\U0002A6DF")},
    {"from": ord(u"\U0002A700"), "to": ord(u"\U0002B73F")},
    {"from": ord(u"\U0002B740"), "to": ord(u"\U0002B81F")},
    {"from": ord(u"\U0002B820"), "to": ord(u"\U0002CEAF")},
    {"from": ord(u"\uF900"), "to": ord(u"\uFAFF")},
    {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
    {"from": ord(u"\uAC00"), "to": ord(u"\uD7AF")},
    {"from": ord(u"\u3041"), "to": ord(u"\u3094")},
    {"from": ord(u"\u3099"), "to": ord(u"\u909E")},
    {"from": ord(u"\u3000"), "to": ord(u"\u303F")}
]

__gradients = [
    ["fad0c4", "ff9a9e"],
    ["fbc2eb", "a18cd1"],
    ["fad0c4", "ffd1ff"],
    ["ff9a9e", "fecfef"],
    ["fdcbf1", "e6dee9"],
    ["fbc2eb", "a6c1ee"],
    ["fccb90", "d57eeb"],
    ["fed6e3", "a8edea"],
    ["fef9d7", "d299c2"],
    ["f6f3ff", "cd9cf2"],
    ["cfc7f8", "ebbba7"],
    ["f5efef", "feada6"],
    ["fbc8d4", "9795f0"],
    ["97d9e1", "d9afd9"],
    ["f3e7e9", "dad4ec"],
    ["ffdde1", "ee9ca7"],
    ["e6dee9", "bdc2e8"],
    ["bfd9fe", "df89b5"]
]

def get_random_gradients():
    a, b = random.choice(__gradients)
    return get_rgb(a), get_rgb(b)

def checkCJK(text: str):
    i = False
    for l in text:
        if any([range["from"] <= ord(l) <= range["to"] for range in __cjk]):
            i = True
            break
    return i

class economy:

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("economy", localedir="locale", languages=[x])

    async def get_cached_user(self, user_id: int):
        cache = await self.bot.redis.get("user_cache:{}".format(user_id))
        if cache is None:
            cache = await self.bot.get_user_info(user_id)
            cache = {
                "name": cache.name,
                "id": cache.id,
                "discriminator": cache.discriminator
            }
            await self.bot.redis.set("user_cache:{}".format(user_id), base64.b64encode(
                json.dumps(cache).encode("utf8")
            ).decode("utf8"), expire=1800)
        else:
            cache = json.loads(base64.b64decode(cache))
        return cache

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

    async def __has_donated(self, user:int):
        data = await self.bot.redis.get("donate:{}".format(user))
        if data:
            return True
        else:
            return False

    # yes i stole this
    def _required_exp(self, level: int):
        if level < 0:
            return 0
        return 139 * level + 65

    def _level_exp(self, level: int):
        return level * 65 + 139 * level * (level - 1) // 2

    def _find_level(self, total_exp):
        return int((1 / 278) * (9 + math.sqrt(81 + 1112 * (total_exp))))

    async def __has_account(self, user:int):
        if await r.table("economy").get(str(user)).run(self.bot.r_conn):
            return True
        else:
            return False

    async def __get_balance(self, user:int):
        balance = await r.table("economy").get(str(user)).run(self.bot.r_conn)
        return int(balance["balance"])

    async def __has_level_account(self, user:int):
        if await r.table("levels").get(str(user)).run(self.bot.r_conn):
            return True
        else:
            return False

    async def __create_level_account(self, user:int):
        data = {
            "id": str(user),
            "info": "",
            "color": "deadbf"
        }
        await r.table("levels").insert(data).run(self.bot.r_conn)

    async def __check_level_account(self, user:int):
        if not await self.__has_level_account(user):
            await self.__create_level_account(user)

    async def __get_rep_data(self, user:int):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get("https://api.weeb.sh/reputation/310039170792030211/%s" % (user,)) as r:
                res = await r.json()
        return res

    async def __update_balance(self, user:int, amount:int):
        await r.table("economy").get(str(user)).update({"balance": int(amount)}).run(self.bot.r_conn)

    async def __update_payday_time(self, user:int):
        await r.table("economy").get(str(user)).update({"lastpayday": str(int(time.time()))}).run(self.bot.r_conn)

    async def __add_bettime(self, user:int):
        try:
            data = await r.table("economy").get(str(user)).run(self.bot.r_conn)
            bettimes = data["bettimes"]
            bettimes.append(str(int(time.time())))
            await r.table("economy").get(str(user)).update({"bettimes": bettimes}).run(self.bot.r_conn)
        except:
            pass

    async def __is_frozen(self, user:int):
        data = await r.table("economy").get(str(user)).run(self.bot.r_conn)
        frozen = data.get("frozen", False)
        if frozen:
            return True
        else:
            return False

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def register(self, ctx):
        """Register an account."""
        user = ctx.author
        _ = await self._get_text(ctx)

        await self.__check_level_account(user.id)

        if await self.__has_account(user.id):
            await ctx.send(_("You already have an account."))
        else:
            data = {
                "id": str(user.id),
                "balance": 0,
                "lastpayday": "0",
                "bettimes": [],
                "frozen": False
            }
            await r.table("economy").insert(data).run(self.bot.r_conn)
            await ctx.send(_("Made an account!"))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx, user:discord.Member=None):
        """Show your or a users balance."""
        _ = await self._get_text(ctx)

        if not user:
            user = ctx.author

        await self.__check_level_account(user.id)

        if await self.__has_account(user.id):
            balance = await self.__get_balance(user.id)
            await ctx.send("💵 | " + _("Balance: **$%s**").replace("$", "￥") % balance)
        else:
            await ctx.send("💵 | " + _("Balance: **$0**").replace("$", "￥"))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def genprofile(self, ctx):
        temp = BytesIO()
        (await self._generate_profile(1000, "test profile", "test description", 500000, [
            "469920504250236948", "270133511325876224", "327144735359762432", "159985870458322944", "160105994217586689"
        ], 5)).save(temp, format="png")
        temp.seek(0)
        await ctx.send(file=discord.File(fp=temp, filename="profile.png"))

    async def _generate_profile(self, xp, username, description, balance, married_to, reputation):
        img = np.zeros((400, 400, 3), np.uint8)
        c1, c2 = get_random_gradients()
        for x, color in enumerate(interpolate(c1, c2, img.shape[1] * 2)):
            cv2.line(img, (x, 0), (0, x), tuple(color), 1)
        cv2.line(img, (25, 130), (375, 130), (0, 0, 0), 1)
        overlay = img.copy()
        cv2.rectangle(overlay, (16, 137), (384, 157), (255, 255, 255), -1)
        cv2.addWeighted(overlay, 0.25, img, 0.75, 0, img)
        overlay = img.copy()
        cv2.rectangle(overlay, (16, 170), (200, 385), (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.07, img, 0.93, 0, img)

        level = self._find_level(xp)
        required_xp = self._level_exp(level + 1)

        xp_percentage = int(xp / required_xp * 100)
        cv2.rectangle(img, (16, 137), (round(3.68 * xp_percentage) + 16, 157), (240, 240, 240), -1)

        img = Image.fromarray(img)
        side_font = ImageFont.truetype("data/fonts/RobotoCondensed/RobotoCondensed-Light.ttf", 25)
        xp_font = ImageFont.truetype("data/fonts/RobotoCondensed/RobotoCondensed-Bold.ttf", 13)
        marriage_title_font = ImageFont.truetype("data/fonts/RobotoCondensed/RobotoCondensed-Light.ttf", 22)
        marriage_user_font = ImageFont.truetype("data/fonts/RobotoCondensed/RobotoCondensed-Light.ttf", 19)
        marriage_user_font_cjk = ImageFont.truetype("data/fonts/Noto/NotoSerifCJKjp-Light.otf", 19)
        draw = ImageDraw.Draw(img)

        if checkCJK(username):
            username_font = ImageFont.truetype("data/fonts/Noto/NotoSerifCJKjp-Light.otf",
                                               33 if len(username) <= 16 else 27)
            w, h = draw.textsize(username, username_font)
            draw.text(((img.width - w) / 2, 85 if len(username) <= 16 else 93), username, 0, username_font)
        else:
            username_font = ImageFont.truetype("data/fonts/Noto/NotoSans-SemiCondensedLight.ttf",
                                               37 if len(username) <= 16 else 33)
            w, h = draw.textsize(username, username_font)
            draw.text(((img.width - w) / 2, 83), username, 0, username_font)

        description = textwrap.fill(description, 20)

        if checkCJK(description):
            description_font = ImageFont.truetype("data/fonts/Noto/NotoSerifCJKjp-Light.otf", 15)
            st = 176
        else:
            description_font = ImageFont.truetype("data/fonts/RobotoCondensed/RobotoCondensed-Light.ttf", 17)
            st = 180

        draw.text((25, st), description, 0, description_font)
        draw.text((22, 139), "%sXP" % xp, (140, 140, 140), xp_font)
        draw.text(((img.width - draw.textsize("Level %s" % level, xp_font)[0]) / 2, 139),
                  "Level %s" % level, (100, 100, 100), xp_font)
        draw.text(({1: 355, 2: 350, 3: 345,
                    4: 337, 5: 328, 6: 320,
                    7: 313, 8: 306, 9: 300}[len(str(required_xp))], 139), "%sXP" % required_xp, (140, 140, 140),
                  xp_font)
        draw.text((210, 175), "¥{:,}".format(balance), 0, ImageFont.truetype("data/fonts/mplus/mplus-2p-light.ttf", 25))
        draw.text((210, 203), "%s Reputation" % reputation, 0, side_font)

        if married_to:
            draw.text((210, 240), "Married to", 0, marriage_title_font)

            for i, userID in enumerate(married_to, start=1):
                try:
                    user = (await self.get_cached_user(userID))["name"]

                    if checkCJK(user):
                        m_font = marriage_user_font_cjk
                        st = 240
                    else:
                        m_font = marriage_user_font
                        st = 245
                    draw.text((210, st + (i * 20)), user, 0, m_font)
                except:
                    draw.text((210, st + (i * 20)), "Unknown User", 0, marriage_user_font)
        else:
            draw.text((210, 240), "Married to nobody", 0, marriage_title_font)

        return img

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx, user: discord.Member=None):
        """Get a users profile, if no user is given it will show your profile instead."""
        await ctx.trigger_typing()

        if user is None:
            user = ctx.author

        await self.__check_level_account(user.id)

        # Level Check
        if not await self.__has_level_account(user.id):
            info = ""
        else:
            userinfo = await r.table("levels").get(str(user.id)).run(self.bot.r_conn)
            info = base64.b64decode(userinfo["info"]).decode("utf8")

        # Economy Check
        if not await self.__has_account(user.id):
            balance = 0
        else:
            balance = await self.__get_balance(user.id)

        # Get Users Reputation
        rep = (await self.__get_rep_data(user.id))["user"]["reputation"]

        # Get Users Level
        xp = await r.table("levelSystem").get(str(user.id)).run(self.bot.r_conn)
        if xp:
            xp = xp["xp"]
        else:
            xp = 0

        # Get users guild level
        # Not needed now
        # _guild_xp = await r.table("guildXP").get(str(ctx.guild.id)).run(self.bot.r_conn)
        # if _guild_xp:
        #     try:
        #         guild_xp = _guild_xp[str(ctx.author.id)]["xp"]
        #     except:
        #         guild_xp = 0
        #     guild_level = self._find_level(guild_xp)
        #     guild_required = self._level_exp(guild_level + 1)
        # else:
        #     guild_xp = 0
        #     guild_level = 0
        #     guild_required = 0

        # Get user married to
        married = await r.table("marriage").get(str(user.id)).run(self.bot.r_conn)
        if married:
            married = married.get("marriedTo", [])
        else:
            married = []

        # em = discord.Embed(color=color)
        #         # em.title = "%s's Profile" % user.name
        #         # wew = (f"${balance}", rep, level, xp, required, guild_level, guild_xp, guild_required, info,)
        #         # em.description = "💵 | Balance: **%s**\n📈 | Rep: **%s**\n🌎 | Level: **%s %s/%s**\n🎮 Server Level: **%s %s/%s**\n\n```\n%s\n```" % wew
        #         # em.set_footer(text="Married to %s" % married)
        #         # em.set_thumbnail(url=user.avatar_url)

        temp = BytesIO()
        (await self._generate_profile(int(xp), user.name, info, int(balance), married, rep)).save(temp, format="png")
        temp.seek(0)

        await ctx.send(file=discord.File(fp=temp, filename="profile.png"))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def daily(self, ctx):
        """Get your daily bonus credits"""
        user = ctx.author
        _ = await self._get_text(ctx)
        await self.__check_level_account(user.id)

        if not await self.__has_account(user.id):
            return await ctx.send(_("You don't have a bank account. Make one with `register`"))

        user_data = await r.table("economy").get(str(user.id)).run(self.bot.r_conn)
        last_payday = user_data["lastpayday"]
        user_balance = int(user_data["balance"])
        if await self.__is_frozen(ctx.author.id):
            return await ctx.send(_("This account is frozen"))

        tn = int(time.time())
        st = int(last_payday)
        tl = tn - st
        if not tl >= 86400:
            i = datetime.timedelta(seconds=86400 - tl)
            d = datetime.datetime(1, 1, 1) + i
            return await ctx.send(_("You have `%s` until your next daily.") % d.strftime("%H:%M:%S"))

        msg = ""
        msg += "Daily Credits\n"
        has_donated = 0
        if await self.__has_donated(ctx.author.id):
            has_donated = int((await self.bot.redis.get("donate:{}".format(ctx.author.id))))
        if has_donated > 0:
            msg += "You have received **25000** credits!"
            await self.__update_payday_time(user.id)
            await self.__update_balance(user.id, user_balance + 25000)
        else:
            msg += "You have received **7500** credits!"
            await self.__update_payday_time(user.id)
            await self.__update_balance(user.id, user_balance + 7500)
        await ctx.send(msg)

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def rep(self, ctx, user:discord.Member):
        """Give a user reputation"""
        _ = await self._get_text(ctx)

        await self.__check_level_account(ctx.author.id)

        if user == ctx.author:
            return await ctx.send(_("You can't give yourself rep"))
        elif user.bot:
            return await ctx.send(_("You can't rep bots"))

        created = int(time.time()) - int(time.mktime(ctx.author.created_at.timetuple()))

        if not created >= 604800:
            return await ctx.send(_("**Your account is too new to give rep.**"))

        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as cs:
            async with cs.post("https://api.weeb.sh/reputation/310039170792030211/%s" % user.id,
                               headers=auth,
                               data={"source_user": str(ctx.author.id)}) as r:
                data = await r.json()

            if data['status'] == 200:
                await ctx.send(_("**%s has given %s 1 reputation point!**") % (ctx.author.name.replace("@", "@\u200B"),
                                                                            user.mention,))
            else:
                async with cs.get("https://api.weeb.sh/reputation/310039170792030211/%s" % ctx.author.id,
                                   headers=auth) as r:
                    repdata = await r.json()
                nextrep = repdata["user"]["nextAvailableReputations"][0]
                timeleft = (datetime.datetime(1, 1, 1) + datetime.timedelta(milliseconds=nextrep)).strftime("%H:%M:%S")
                await ctx.send(_("**%s, you can give more reputation in `%s`**") % (ctx.author.mention, timeleft,))

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def setdesc(self, ctx, *, description:str):
        """Set your profile description"""
        await self.__check_level_account(ctx.author.id)
        _ = await self._get_text(ctx)

        if len(description) > 500:
            return await ctx.send(_("Your description is too long."))

        description = base64.b64encode(description.encode("utf8")).decode("utf8")
        await r.table("levels").get(str(ctx.author.id)).update({"info": description}).run(self.bot.r_conn)
        await ctx.send(_("Updated Description!"))

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.guild_only()
    async def coinflip(self, ctx, amount:int):
        """Coinflip!"""
        await self.__check_level_account(ctx.author.id)
        _ = await self._get_text(ctx)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send(_("You don't have an account, you can make one with `register`"))

        if await self.__is_frozen(ctx.author.id):
            return await ctx.send(_("This account is frozen"))

        if amount <= 0:
            return await ctx.send(_("Your amount must be higher than 0"))
        elif amount > 100000:
            return await ctx.send(_("You can't bet past 100,000"))

        balance = await self.__get_balance(ctx.author.id)

        if (balance - amount) < 0:
            return await ctx.send(_("You don't have that much to spend"))

        msg = await ctx.send(_("Flipping..."))
        await asyncio.sleep(random.randint(1, 5))

        choice = random.randint(0, 1)

        em = discord.Embed(color=0xDEADBF)
        await self.__add_bettime(ctx.author.id)

        if choice == 1:
            em.title = _("You Won!")
            em.description = _("You won `%s`!") % int(amount * .5)
            await self.__update_balance(ctx.author.id, balance + int(amount * .5))
        else:
            em.title = _("You Lost")
            em.description = _("You lost `%s`") % amount
            await self.__update_balance(ctx.author.id, balance - amount)

        await msg.edit(content=None, embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def top(self, ctx):
        """Get top economy users."""
        await self.__check_level_account(ctx.author.id)
        await ctx.trigger_typing()

        table = PrettyTable()
        table.field_names = ["Username", "Balance"]

        for i in range(10):
            username = (await self.bot.redis.get("top%s:name" % i))
            balance = (await self.bot.redis.get("top%s" % i))
            table.add_row([username.decode("utf8"), balance.decode("utf8")])

        await ctx.send("```\n%s\n```" % table)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def transfer(self, ctx, user: discord.Member, amount: int):
        """Transfer money to another user"""
        _ = await self._get_text(ctx)

        await self.__check_level_account(ctx.author.id)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send(_("You don't have an account, you can create one with `register`"))
        elif not await self.__has_account(user.id):
            return await ctx.send(_("`%s` doesn't have an account, they can create one with `register`") % user.name)

        if await self.__is_frozen(ctx.author.id):
            return await ctx.send(_("This account is frozen"))
        if await self.__is_frozen(user.id):
            return await ctx.send(_("The user you are sending to has a frozen account."))

        if amount < 10:
            return await ctx.send(_("The amount must be higher than 10"))
        elif amount > 10000000:
            return await ctx.send(_("You can't send more than $10 million at a time.").replace("$", "￥"))
        if user.bot:
            return await ctx.send(_("You can't send bots money"))
        elif user == ctx.author:
            return await ctx.send(_("You can't send yourself money"))

        author_balance = await self.__get_balance(ctx.author.id)
        user_balance = await self.__get_balance(user.id)

        if (author_balance - amount) < 0:
            return await ctx.send(_("You don't have that much to spend."))

        await self.__update_balance(user.id, user_balance + amount)
        await self.__update_balance(ctx.author.id, author_balance - amount)

        await ctx.send(_("Successfully sent %s $%s").replace("$", "￥") % (user.name, amount,))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def roulette(self, ctx, amount: int, color: str):
        _ = await self._get_text(ctx)

        await self.__check_level_account(ctx.author.id)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send(_("You don't have a bank account..."))

        if await self.__is_frozen(ctx.author.id):
            return await ctx.send(_("This account is frozen"))

        author_balance = await self.__get_balance(ctx.author.id)

        if amount <= 0:
            return await ctx.send(_("You can't bet that low..."))
        if (author_balance - amount) < 0:
            return await ctx.send(_("You don't have that much to bet..."))
        if amount > 75000:
            return await ctx.send(_("You can't bet past 75k"))

        color = color.lower()
        if color not in ["red", "green", "black"]:
            return await ctx.send(_("Invalid color, available colors: `red`, `black`, `green`"))

        await self.__update_balance(ctx.author.id, author_balance - amount)
        await self.__add_bettime(ctx.author.id)

        choice = random.randint(0, 36)

        if choice in [32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10]:
            chosen_color = "red"
        elif choice in [5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]:
            chosen_color = "black"
        else:
            chosen_color = "green"

        if chosen_color != color:
            return await ctx.send(_("It landed on `%s`, you lost :c") % chosen_color)
        else:
            if chosen_color == "green":
                await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 36))
                return await ctx.send("You hit green!")
            await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))
            return await ctx.send(_("It landed on `%s` and you won!") % choice)

    async def delmsg(self, msg: discord.Message):
        try:
            await msg.delete()
        except:
            pass

    # holy
    # fuck
    # shit
    # code
    # ahead
    # beware
    # !
    # !
    # !
    # !
    # for loops when
    @commands.command(aliases=['bj'])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blackjack(self, ctx, amount: int):
        """Blackjack"""
        author = ctx.author
        _ = await self._get_text(ctx)

        await self.__check_level_account(author.id)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send(_("You don't have a bank account..."))

        if await self.__is_frozen(ctx.author.id):
            return await ctx.send(_("This account is frozen"))

        author_balance = await self.__get_balance(ctx.author.id)

        if amount <= 0:
            await ctx.send(_("You can't bet that low..."))
            return
        if (author_balance - amount) < 0:
            await ctx.send(_("You don't have that much to bet..."))
            return
        if amount > 50000:
            await ctx.send(_("You can't bet past 50k"))
            return

        await self.__update_balance(ctx.author.id, author_balance - amount)
        await self.__add_bettime(ctx.author.id)

        card_list = {
            "2": "<:2C:424587135463456778>",
            "3": "<:3C:424587163737522176>",
            "4": "<:4C:424587171232743425>",
            "5": "<:5C:424587178933223425>",
            "6": "<:6C:424587180938231808>",
            "7": "<:7C:424587184650059779>",
            "8": "<:8C:424587186160271400>",
            "9": "<:9C:424587184717168640>",
            "10": "<:10C:424587186055151617>",
            "11": "<:AC:424587167864717313>",
            "K": "<:KC:424587233182351362>",
            "Q": "<:QC:424587235715973130>",
            "J": "<:JC:424587235673767966>"
        }
        special = ["K", "Q", "J"]

        cards = [card for card in card_list]

        author_deck = []
        bot_deck = []
        author_deck_n = []
        bot_deck_n = []
        hasHit_author = False
        hasHit_bot = False
        author_card_amount = 0
        bot_card_amount = 0

        while True:
            card = random.choice(cards)
            if card not in author_deck:
                author_deck.append(card)
                if card in special:
                    card = 10
                if card == "11":
                    if not hasHit_author or not author_card_amount > 11:
                        card = 11
                        hasHit_author = True
                    else:
                        card = 1
                author_card_amount += int(card)
                author_deck_n.append(card)
            if len(author_deck) == 5:
                break

        while True:
            card = random.choice(cards)
            if card not in bot_deck:
                bot_deck.append(card)
                if card in special:
                    card = 10
                if card == "11":
                    if not hasHit_bot or not bot_card_amount > 11:
                        card = 11
                        hasHit_bot = True
                    else:
                        card = 1
                bot_card_amount += int(card)
                bot_deck_n.append(card)
            if len(bot_deck) == 5:
                break

        win_embed = discord.Embed(color=0xDEADBF)
        win_embed.title = _("Blackjack Win")
        win_embed.description = _("**%s** (%s) has won %s") % (ctx.author.name, ctx.author.id, int(amount * .75))

        lose_embed = discord.Embed(color=0xDEADBF)
        lose_embed.title = _("Blackjack Lose")
        lose_embed.description = _("**%s** (%s) has lost %s") % (ctx.author.name, ctx.author.id, int(amount))

        em = discord.Embed(color=0xDEADBF)
        em.title = _("Blackjack")
        em.description = _("Type `hit` or `stay`.")
        author_value = "%s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                           card_list[author_deck[1]], author_deck_n[1],)
        bot_value = "%s %s | ? ?" % (card_list[bot_deck[0]], bot_deck_n[0])
        author_total = int(author_deck_n[0]) + int(author_deck_n[1])
        bot_total = int(bot_deck_n[0]) + int(bot_deck_n[1])
        em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
        em.add_field(name=_("My Cards (?)"), value=bot_value, inline=True)

        msg = await ctx.send(embed=em)

        def check(m):
            return m.channel == ctx.message.channel and m.author == author

        while True:
            x = await self.bot.wait_for('message', check=check)

            if str(x.content).lower() == "hit":
                move = 0
                break
            elif str(x.content).lower() == "stay":
                move = 1
                break
            else:
                pass
        await self.delmsg(x)

        if move == 1:
            em = discord.Embed(color=0xDEADBF)
            em.title = _("Blackjack")

            author_value = "%s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                               card_list[author_deck[1]], author_deck_n[1],)
            bot_value = "%s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                            card_list[bot_deck[1]], bot_deck_n[1])

            if author_total > bot_total:
                em.description = _("You beat me!")
                em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
                em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)
                await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))
            else:
                em.description = _("I beat you >:3")
                em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
                em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        author_total = int(author_deck_n[0]) + int(author_deck_n[1]) + int(author_deck_n[2])
        bot_total = int(bot_deck_n[0]) + int(bot_deck_n[1]) + int(bot_deck_n[2])

        author_value = f"%s %s | %s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                                   card_list[author_deck[1]], author_deck_n[1],
                                                   card_list[author_deck[2]], author_deck_n[2],)
        bot_value = f"%s %s | ? ? | ? ?" % (card_list[bot_deck[0]], bot_deck_n[0])

        if author_total > 21 or bot_total > 21:
            em = discord.Embed(color=0xDEADBF)
            em.title = _("Blackjack")

            if author_total > 21:
                em.description = _("You went over 21 and I won >:3")

            else:
                em.description = _("I went over 21 and you won ;w;")
                await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))

            bot_value = f"%s %s | %s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                                    card_list[bot_deck[1]], bot_deck_n[1],
                                                    card_list[bot_deck[2]], bot_deck_n[2],)

            em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
            em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        em = discord.Embed(color=0xDEADBF)
        em.title = _("Blackjack")
        em.description = _("Type `hit` or `stay`.")
        em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
        em.add_field(name=_("My Cards (?)"), value=bot_value, inline=True)
        await msg.edit(embed=em)

        while True:
            x = await self.bot.wait_for('message', check=check)

            if str(x.content).lower() == "hit":
                move = 0
                break
            elif str(x.content).lower() == "stay":
                move = 1
                break
            else:
                pass
        await self.delmsg(x)

        if move == 1:
            em = discord.Embed(color=0xDEADBF)
            em.title = _("Blackjack")

            if author_total > bot_total:
                em.description = _("You beat me!")
                em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
                em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)
                await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))
            else:
                em.description = _("I beat you >:3")
                em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
                em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)
            return await msg.edit(embed=em)

        author_total = int(author_deck_n[0]) + int(author_deck_n[1]) + int(author_deck_n[2]) + int(author_deck_n[3])
        bot_total = int(bot_deck_n[0]) + int(bot_deck_n[1]) + int(bot_deck_n[2]) + int(bot_deck_n[3])

        author_value = f"%s %s | %s %s | %s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                                           card_list[author_deck[1]], author_deck_n[1],
                                                           card_list[author_deck[2]], author_deck_n[2],
                                                           card_list[author_deck[3]], author_deck_n[3],)
        bot_value = f"%s %s | ? ? | ? ? | ? ?" % (card_list[bot_deck[0]], bot_deck_n[0])

        if author_total > 21 or bot_total > 21:
            em = discord.Embed(color=0xDEADBF)
            em.title = _("Blackjack")

            if author_total > 21:
                em.description = _("You went over 21 and I won >:3")

            else:
                em.description = _("I went over 21 and you won ;w;")
                await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))

            bot_value = f"%s %s | %s %s | %s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                                            card_list[bot_deck[1]], bot_deck_n[1],
                                                            card_list[bot_deck[2]], bot_deck_n[2],
                                                            card_list[bot_deck[3]], bot_deck_n[3],)

            em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
            em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        em = discord.Embed(color=0xDEADBF)
        em.title = _("Blackjack")
        em.description = _("Type `hit` or `stay`.")
        em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
        em.add_field(name=_("My Cards (?)"), value=bot_value, inline=True)
        await msg.edit(embed=em)

        while True:
            x = await self.bot.wait_for('message', check=check)

            if str(x.content).lower() == "hit":
                move = 0
                break
            elif str(x.content).lower() == "stay":
                move = 1
                break
            else:
                pass
        await self.delmsg(x)

        if move == 1:
            em = discord.Embed(color=0xDEADBF)
            em.title = _("Blackjack")

            if author_total > bot_total:
                em.description = _("You beat me!")
                em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
                em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)
                await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))
            else:
                em.description = _("I beat you >:3")
                em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
                em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        author_total = int(author_deck_n[0]) + int(author_deck_n[1]) + int(author_deck_n[2]) + int(author_deck_n[3]) + \
                       int(author_deck_n[4])
        bot_total = int(bot_deck_n[0]) + int(bot_deck_n[1]) + int(bot_deck_n[2]) + int(bot_deck_n[3]) + \
                    int(bot_deck_n[4])

        author_value = f"%s %s | %s %s | %s %s | %s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                                                   card_list[author_deck[1]], author_deck_n[1],
                                                                   card_list[author_deck[2]], author_deck_n[2],
                                                                   card_list[author_deck[3]], author_deck_n[3],
                                                                   card_list[author_deck[4]], author_deck_n[4],)

        if author_total > 21 or bot_total > 21:
            em = discord.Embed(color=0xDEADBF)
            em.title = _("Blackjack")

            if author_total > 21:
                em.description = _("You went over 21 and I won >:3")

            else:
                em.description = _("I went over 21 and you won ;w;")
                await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))

            bot_value = f"%s %s | %s %s | %s %s | %s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                                                    card_list[bot_deck[1]], bot_deck_n[1],
                                                                    card_list[bot_deck[2]], bot_deck_n[2],
                                                                    card_list[bot_deck[3]], bot_deck_n[3],
                                                                    card_list[bot_deck[4]], bot_deck_n[4],)

            em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
            em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        em = discord.Embed(color=0xDEADBF)
        em.title = _("Blackjack")

        if author_total > bot_total:
            em.description = _("You beat me ;w;")
            await self.__update_balance(ctx.author.id, (await self.__get_balance(ctx.author.id)) + int(amount * 1.75))
        else:
            em.description = _("I beat you >:3")

        em.add_field(name=_("Your Cards (%s)") % author_total, value=author_value, inline=True)
        em.add_field(name=_("My Cards (%s)") % bot_total, value=bot_value, inline=True)
        return await msg.edit(embed=em)

    # async def __handle_guild_xp(self, guild:int, user:int):
    #     if not await r.table("guildXP").get(str(guild)).run(self.bot.r_conn):
    #         data = {
    #             "id": str(guild)
    #         }
    #         await r.table("guildXP").insert(data).run(self.bot.r_conn)
    #
    #     guild_data = await r.table("guildXP").get(str(guild)).run(self.bot.r_conn)
    #
    #     user_exists = guild_data.get(str(user), None)
    #
    #     if not user_exists:
    #         data = {
    #             str(user): {
    #                 "xp": 0,
    #                 "lastxp": "0"
    #             }
    #         }
    #     else:
    #         data = {
    #             str(user): {
    #                 "xp": guild_data[str(user)]["xp"] + random.randint(1, 30),
    #                 "lastxp": str(int(time.time()))
    #             }
    #         }
    #
    #     await r.table("guildXP").get(str(guild)).update(data).run(self.bot.r_conn)

def setup(bot):
    bot.add_cog(economy(bot))