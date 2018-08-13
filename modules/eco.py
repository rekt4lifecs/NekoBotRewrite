import rethinkdb as r
from discord.ext import commands
import discord
from config import weeb, dbots_key
import aiohttp, asyncio
import base64, random
import datetime, time, math
from prettytable import PrettyTable
import hooks

auth = {"Authorization": "Wolke " + weeb,
        "User-Agent": "NekoBot/4.2.0"}

# Todo languages

class economy:

    def __init__(self, bot):
        self.bot = bot

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

    async def __has_voted(self, user:int):
        if await r.table("votes").get(str(user)).run(self.bot.r_conn):
            return True
        else:
            return False

    async def __update_balance(self, user:int, amount:int):
        await r.table("economy").get(str(user)).update({"balance": int(amount)}).run(self.bot.r_conn)

    async def __update_payday_time(self, user:int):
        await r.table("economy").get(str(user)).update({"lastpayday": str(int(time.time()))}).run(self.bot.r_conn)

    async def __post_to_hook(self, action:str, user:discord.Member, amount):
        try:
            async with aiohttp.ClientSession() as cs:
                webhook = discord.Webhook.from_url(hooks.get_url(), adapter=discord.AsyncWebhookAdapter(cs))
                await webhook.send("User: %s (%s)\nAction: %s\nAmount: %s\nTime: %s" % (str(user), user.id, action, amount, int(time.time())))
        except:
            pass

    async def __add_bettime(self, user:int):
        data = await r.table("economy").get(str(user)).run(self.bot.r_conn)
        bettimes = data["bettimes"]
        bettimes.append(str(int(time.time())))
        await r.table("economy").get(str(user)).update({"bettimes": bettimes}).run(self.bot.r_conn)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def register(self, ctx):
        """Register an account."""
        user = ctx.author

        await self.__check_level_account(user.id)

        if await self.__has_account(user.id):
            await ctx.send("You already have an account.")
        else:
            data = {
                "id": str(user.id),
                "balance": 0,
                "lastpayday": "0",
                "bettimes": []
            }
            await self.__post_to_hook("Register", ctx.author, 0)
            await r.table("economy").insert(data).run(self.bot.r_conn)
            await ctx.send("Made an account!")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx, user:discord.Member=None):
        """Show your or a users balance."""

        if not user:
            user = ctx.author

        await self.__check_level_account(user.id)

        if await self.__has_account(user.id):
            balance = await self.__get_balance(user.id)
            await ctx.send("💵 | Balance: **$%s**" % balance)
        else:
            await ctx.send("💵 | Balance: **$0**")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx, user:discord.Member=None):
        """Get a users profile, if no user is given it will show your profile instead."""
        await ctx.trigger_typing()

        if user is None:
            user = ctx.author

        await self.__check_level_account(user.id)

        # Level Check
        if not await self.__has_level_account(user.id):
            info = ""
            color = int("deadbf", 16)
        else:
            userinfo = await r.table("levels").get(str(user.id)).run(self.bot.r_conn)
            info = base64.b64decode(userinfo["info"]).decode("utf8")
            color = int(userinfo["color"], 16)

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
            level = self._find_level(xp)
            required = self._level_exp(level + 1)
        else:
            xp = 0
            level = 0
            required = 0

        # Get user married to
        married = await r.table("marriage").get(str(user.id)).run(self.bot.r_conn)
        if not married:
            married = "Nobody"
        else:
            married = await self.bot.get_user_info(married["marriedTo"])

        em = discord.Embed(color=color)
        em.title = "%s's Profile" % user.name
        wew = (f"${balance}", rep, level, xp, required, info,)
        em.description = "💵 | Balance: **%s**\n📈 | Rep: **%s**\n🎮 | Level: **%s %s/%s**\n\n```\n%s\n```" % wew
        em.set_footer(text="Married to %s" % married)
        em.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def daily(self, ctx):
        """Get your daily bonus credits"""
        user = ctx.author
        await self.__check_level_account(user.id)

        if not await self.__has_account(user.id):
            return await ctx.send("You don't have a bank account. Make one with `register`")

        user_data = await r.table("economy").get(str(user.id)).run(self.bot.r_conn)
        last_payday = user_data["lastpayday"]
        user_balance = int(user_data["balance"])

        # Get the current day now
        today = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
        # Get the day of the last payday
        payday_day = datetime.datetime.utcfromtimestamp(int(last_payday)).strftime("%d")

        if today == payday_day: # If the last payday was today
            tommorow = datetime.datetime.now() + datetime.timedelta(1)
            midnight = datetime.datetime(year=tommorow.year, month=tommorow.month,
                                         day=tommorow.day, hour=0, minute=0, second=0)
            m, s = divmod((midnight - datetime.datetime.now()).seconds, 60)
            h, m = divmod(m, 60)
            return await ctx.send("You have %s hours and %s minutes until your next daily." % (h, m,))

        if await self.__has_voted(user.id): # If user has voted
            em = discord.Embed(color=0xDEADBF)
            em.title = "Daily Voter Bonus"
            weekday = datetime.datetime.today().weekday()
            if weekday <= 4: # If its a weekend, give weekend bonus.
                em.description = "You have received **12500** weekend bonus credits!"
                await self.__post_to_hook("Daily (Vote Weekend)", ctx.author, 12500)
                await self.__update_payday_time(user.id)
                await self.__update_balance(user.id, user_balance + 12500)
            else:
                em.description = "You have received **7500** credits!"
                await self.__post_to_hook("Daily (Vote)", ctx.author, 7500)
                await self.__update_payday_time(user.id)
                await self.__update_balance(user.id, user_balance + 7500)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(color=0xDEADBF)
            em.title = "Daily Bonus"
            em.description = "You have received **2500** credits!"
            em.set_footer(text="Voting will give you 7500 👀")
            await self.__post_to_hook("Daily (Non Vote)", ctx.author, 2500)
            await self.__update_payday_time(user.id)
            await self.__update_balance(user.id, user_balance + 2500)
            await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def rep(self, ctx, user:discord.Member):
        """Give a user reputation"""

        await self.__check_level_account(ctx.author.id)

        if user == ctx.author:
            return await ctx.send("You can't give yourself rep")
        elif user.bot:
            return await ctx.send("You can't rep bots")

        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as cs:
            async with cs.post("https://api.weeb.sh/reputation/310039170792030211/%s" % user.id,
                               headers={"Authorization": "Wolke " + weeb},
                               data={"source_user": str(ctx.author.id)}) as r:
                data = await r.json()

            if data['status'] == 200:
                await ctx.send("**%s has given %s 1 reputation point!**" % (ctx.author.name.replace("@", "@\u200B"),
                                                                            user.mention,))
            else:
                async with cs.get("https://api.weeb.sh/reputation/310039170792030211/%s" % ctx.author.id,
                                   headers={"Authorization": "Wolke " + weeb}) as r:
                    repdata = await r.json()
                nextrep = repdata["user"]["nextAvailableReputations"][0]
                timeleft = str(datetime.timedelta(milliseconds=nextrep)).rpartition(".")[0]
                await ctx.send("**%s, you can give more reputation in %s**" % (ctx.author.mention, timeleft,))

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def setdesc(self, ctx, *, description:str):
        """Set your profile description"""
        await self.__check_level_account(ctx.author.id)

        if len(description) > 500:
            return await ctx.send("Your description is too long.")

        description = base64.b64encode(description.encode("utf8")).decode("utf8")
        await r.table("levels").get(str(ctx.author.id)).update({"info": description}).run(self.bot.r_conn)
        await ctx.send("Updated Description!")

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.guild_only()
    async def coinflip(self, ctx, amount:int):
        """Coinflip!"""
        await self.__check_level_account(ctx.author.id)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send("You don't have an account, you can make one with `register`")

        if amount <= 0:
            return await ctx.send("Your amount must be higher than 0")
        elif amount > 100000:
            return await ctx.send("You can't bet past 100,000")

        balance = await self.__get_balance(ctx.author.id)

        if (balance - amount) < 0:
            return await ctx.send("You don't have that much to spend")

        msg = await ctx.send("Flipping...")
        await asyncio.sleep(random.randint(1, 5))

        choice = random.randint(0, 1)

        em = discord.Embed(color=0xDEADBF)
        await self.__add_bettime(ctx.author.id)

        if choice == 1:
            em.title = "You Won!"
            em.description = "You won `%s`!" % int(amount * .5)
            await self.__post_to_hook("Coinflip Win", ctx.author, int(amount * .5))
            await self.__update_balance(ctx.author.id, balance + int(amount * .5))
        else:
            em.title = "You Lost"
            em.description = "You lost `%s`" % amount
            await self.__post_to_hook("Coinflip Loss", ctx.author, amount)
            await self.__update_balance(ctx.author.id, balance - amount)

        await msg.edit(content=None, embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def top(self, ctx):
        """Get top economy users."""
        await self.__check_level_account(ctx.author.id)
        await ctx.trigger_typing()

        table = PrettyTable()
        table.field_names = ["Username", "Balance"]

        top_users = await r.table("economy").order_by(r.desc("balance")).limit(10).run(self.bot.r_conn)

        for user in top_users:
            try:
                username = str(await self.bot.get_user_info(int(user["id"])))
            except:
                username = "Unknown User"
            balance = user["balance"]
            table.add_row([username, balance])

        await ctx.send("```\n%s\n```" % table)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def transfer(self, ctx, user: discord.Member, amount: int):
        """Transfer money to another user"""

        await self.__check_level_account(ctx.author.id)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send("You don't have an account, you can create one with `register`")
        elif not await self.__has_account(user.id):
            return await ctx.send("`%s` doesn't have an account, they can create one with `register`" % user.name)

        if amount < 10:
            return await ctx.send("The amount must be higher than 10")
        elif amount > 10000000:
            return await ctx.send("You can't send more than $10 million at a time.")
        if user.bot:
            return await ctx.send("You can't send bots money")
        elif user == ctx.author:
            return await ctx.send("You can't send yourself money")

        author_balance = await self.__get_balance(ctx.author.id)
        user_balance = await self.__get_balance(user.id)

        if (author_balance - amount) < 0:
            return await ctx.send("You don't have that much to spend.")

        await self.__update_balance(user.id, user_balance + amount)
        await self.__update_balance(ctx.author.id, author_balance - amount)
        await self.__post_to_hook("Transfer", ctx.author, "%s to %s (%s)" % (amount, str(user), user.id))

        await ctx.send("Successfully sent %s $%s" % (user.name, amount,))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def roulette(self, ctx, amount: int, color: str):

        await self.__check_level_account(ctx.author.id)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send("You don't have a bank account...")

        author_balance = await self.__get_balance(ctx.author.id)

        if amount <= 0:
            return await ctx.send("You can't bet that low...")
        if (author_balance - amount) < 0:
            return await ctx.send("You don't have that much to bet...")
        if amount > 75000:
            return await ctx.send("You can't bet past 75k")

        color = color.lower()
        if color not in ["red", "green", "black"]:
            return await ctx.send("Invalid color, available colors: `red`, `black`, `green`")

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
            await self.__post_to_hook("Roulette Loss", ctx.author, amount)
            return await ctx.send(f"It landed on `{chosen_color}`, you lost :c")
        else:
            if chosen_color == "green":
                await self.__post_to_hook("Roulette Won (green)", ctx.author, int(amount*36))
                await self.__update_balance(ctx.author.id, author_balance + int(amount * 36))
                return await ctx.send("You hit green!")
            await self.__post_to_hook("Roulette Won (%s)" % color, ctx.author, int(amount*.75))
            await self.__update_balance(ctx.author.id, author_balance + int(amount * .75))
            return await ctx.send(f"It landed on `{chosen_color}` and you won!")

    async def delmsg(self, msg: discord.Message):
        try:
            await msg.delete()
        except:
            pass

    @commands.command(aliases=['bj'])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blackjack(self, ctx, amount: int):
        """Blackjack"""
        author = ctx.author

        await self.__check_level_account(author.id)

        if not await self.__has_account(ctx.author.id):
            return await ctx.send("You don't have a bank account...")

        author_balance = await self.__get_balance(ctx.author.id)

        if amount <= 0:
            await ctx.send("You can't bet that low...")
            return
        if (author_balance - amount) < 0:
            await ctx.send("You don't have that much to bet...")
            return
        if amount > 50000:
            await ctx.send("You can't bet past 50k")
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
        win_embed.title = "Blackjack Win"
        win_embed.description = "**%s** (%s) has won %s" % (ctx.author.name, ctx.author.id, int(amount * .75))

        lose_embed = discord.Embed(color=0xDEADBF)
        lose_embed.title = "Blackjack Lose"
        lose_embed.description = "**%s** (%s) has lost %s" % (ctx.author.name, ctx.author.id, int(amount))

        em = discord.Embed(color=0xDEADBF)
        em.title = "Blackjack"
        em.description = "Type `hit` or `stay`."
        author_value = f"%s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                           card_list[author_deck[1]], author_deck_n[1],)
        bot_value = f"%s %s | ? ?" % (card_list[bot_deck[0]], bot_deck_n[0])
        author_total = int(author_deck_n[0]) + int(author_deck_n[1])
        bot_total = int(bot_deck_n[0]) + int(bot_deck_n[1])
        em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
        em.add_field(name="My Cards (?)", value=bot_value, inline=True)

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
            em.title = "Blackjack"

            author_value = f"%s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                               card_list[author_deck[1]], author_deck_n[1],)
            bot_value = f"%s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                            card_list[bot_deck[1]], bot_deck_n[1])

            if author_total > bot_total:
                em.description = "You beat me!"
                await self.__post_to_hook("Blackjack Won", ctx.author, amount)
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.__update_balance(ctx.author.id, author_balance + int(amount * .5))
            else:
                em.description = "I beat you >:3"
                await self.__post_to_hook("Blackjack Loss", ctx.author, amount)
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        author_total = int(author_deck_n[0]) + int(author_deck_n[1]) + int(author_deck_n[2])
        bot_total = int(bot_deck_n[0]) + int(bot_deck_n[1]) + int(bot_deck_n[2])

        author_value = f"%s %s | %s %s | %s %s" % (card_list[author_deck[0]], author_deck_n[0],
                                                   card_list[author_deck[1]], author_deck_n[1],
                                                   card_list[author_deck[2]], author_deck_n[2],)
        bot_value = f"%s %s | ? ? | ? ?" % (card_list[bot_deck[0]], bot_deck_n[0])

        if author_total > 21 or bot_total > 21:
            em = discord.Embed(color=0xDEADBF)
            em.title = "Blackjack"

            if author_total > 21:
                em.description = "You went over 21 and I won >:3"
                await self.__post_to_hook("Blackjack Loss", ctx.author, amount)

            else:
                em.description = "I went over 21 and you won ;w;"
                await self.__post_to_hook("Blackjack Won", ctx.author, amount)
                await self.__update_balance(ctx.author.id, author_balance + int(amount * .75))

            bot_value = f"%s %s | %s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                                    card_list[bot_deck[1]], bot_deck_n[1],
                                                    card_list[bot_deck[2]], bot_deck_n[2],)

            em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
            em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        em = discord.Embed(color=0xDEADBF)
        em.title = "Blackjack"
        em.description = "Type `hit` or `stay`."
        em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
        em.add_field(name="My Cards (?)", value=bot_value, inline=True)
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
            em.title = "Blackjack"

            if author_total > bot_total:
                em.description = "You beat me!"
                await self.__post_to_hook("Blackjack Won", ctx.author, amount)
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.__update_balance(ctx.author.id, author_balance + int(amount * .75))
            else:
                em.description = "I beat you >:3"
                await self.__post_to_hook("Blackjack Loss", ctx.author, amount)
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
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
            em.title = "Blackjack"

            if author_total > 21:
                em.description = "You went over 21 and I won >:3"
                await self.__post_to_hook("Blackjack Loss", ctx.author, amount)

            else:
                em.description = "I went over 21 and you won ;w;"
                await self.__post_to_hook("Blackjack Won", ctx.author, amount)
                await self.__update_balance(ctx.author.id, author_balance + int(amount * .75))

            bot_value = f"%s %s | %s %s | %s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                                            card_list[bot_deck[1]], bot_deck_n[1],
                                                            card_list[bot_deck[2]], bot_deck_n[2],
                                                            card_list[bot_deck[3]], bot_deck_n[3],)

            em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
            em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        em = discord.Embed(color=0xDEADBF)
        em.title = "Blackjack"
        em.description = "Type `hit` or `stay`."
        em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
        em.add_field(name="My Cards (?)", value=bot_value, inline=True)
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
            em.title = "Blackjack"

            if author_total > bot_total:
                em.description = "You beat me!"
                await self.__post_to_hook("Blackjack Won", ctx.author, amount)
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.__update_balance(ctx.author.id, author_balance + int(amount * .75))
            else:
                em.description = "I beat you >:3"
                await self.__post_to_hook("Blackjack Loss", ctx.author, amount)
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)

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
            em.title = "Blackjack"

            if author_total > 21:
                em.description = "You went over 21 and I won >:3"
                await self.__post_to_hook("Blackjack Loss", ctx.author, amount)

            else:
                em.description = "I went over 21 and you won ;w;"
                await self.__post_to_hook("Blackjack Won", ctx.author, amount)
                await self.__update_balance(ctx.author.id, author_balance + int(amount * .75))

            bot_value = f"%s %s | %s %s | %s %s | %s %s | %s %s" % (card_list[bot_deck[0]], bot_deck_n[0],
                                                                    card_list[bot_deck[1]], bot_deck_n[1],
                                                                    card_list[bot_deck[2]], bot_deck_n[2],
                                                                    card_list[bot_deck[3]], bot_deck_n[3],
                                                                    card_list[bot_deck[4]], bot_deck_n[4],)

            em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
            em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)

            return await msg.edit(embed=em)

        em = discord.Embed(color=0xDEADBF)
        em.title = "Blackjack"

        if author_total > bot_total:
            em.description = "You beat me ;w;"
            await self.__post_to_hook("Blackjack Won", ctx.author, amount)
            await self.__update_balance(ctx.author.id, author_balance + int(amount * .75))
        else:
            em.description = "I beat you >:3"
            await self.__post_to_hook("Blackjack Loss", ctx.author, amount)

        em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
        em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
        return await msg.edit(embed=em)

    async def on_message(self, message):
        if message.author.bot:
            return
        if random.randint(1, 7) == 1:
            if not len(message.content) > 5:
                return
            author = message.author
            if not await r.table("levelSystem").get(str(author.id)).run(self.bot.r_conn):
                data = {
                    "id": str(author.id),
                    "xp": 0,
                    "lastxp": "0",
                    "blacklisted": False,
                    "lastxptimes": []
                }
                await r.table("levelSystem").insert(data).run(self.bot.r_conn)
            user_data = await r.table("levelSystem").get(str(author.id)).run(self.bot.r_conn)
            if user_data["blacklisted"]:
                return
            if (int(time.time()) - int(user_data["lastxp"])) >= 120:
                lastxptimes = user_data["lastxptimes"]
                lastxptimes.append(str(int(time.time())))

                newxp = random.randint(1, 25)
                xp = user_data["xp"] + newxp
                data = {
                    "xp": xp,
                    "lastxp": str(int(time.time())),
                    "lastxptimes": lastxptimes
                }
                await r.table("levelSystem").get(str(author.id)).update(data).run(self.bot.r_conn)

def setup(bot):
    bot.add_cog(economy(bot))