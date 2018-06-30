from discord.ext import commands
import discord, aiohttp, asyncio, datetime, config, random, math, logging
import time
import ujson
from prettytable import PrettyTable

log = logging.getLogger("NekoBot")

# Languages
languages = ["english", "weeb", "tsundere", "polish"]
lang = {}

for l in languages:
    with open("lang/%s.json" % l, encoding="utf-8") as f:
        lang[l] = ujson.load(f)

def getlang(la:str):
    return lang.get(la, None)

class economy:
    """Economy"""

    def __init__(self, bot):
        self.bot = bot

    async def has_account(self, user:discord.Member):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if not await db.execute("SELECT 1 FROM economy WHERE userid = %s", (user,)):
                    return False
                else:
                    return True

    async def has_level_account(self, user:discord.Member):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if not await db.execute("SELECT 1 FROM levels WHERE userid = %s", (user,)):
                    return False
                else:
                    return True

    async def get_balance(self, user:discord.Member):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute("SELECT balance FROM economy WHERE userid = %s", (user,))
                bal = int((await db.fetchone())[0])
                return bal

    async def has_voted(self, user:discord.Member):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if await db.execute("SELECT 1 FROM dbl WHERE user = %s", (user,)):
                    return True
                else:
                    return False

    async def _levels_create_account(self, user:discord.Member):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute("INSERT INTO levels VALUES (%s, 0, 0, 0, 0, 0, 0)", (user,))

    async def edit_balance(self, user:discord.Member, amount:int):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute("UPDATE economy SET balance = %s WHERE userid = %s", (amount, user,))

    async def _economy_create_account(self, user:discord.Member):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute("INSERT INTO economy VALUES (%s, 0, 0)", (user,))

    async def update_payday_time(self, user:discord.Member):
        user = user.id
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute("UPDATE economy SET payday = %s WHERE userid = %s", (int(time.time()), user,))

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
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if not await self.has_level_account(ctx.author):
            await self._levels_create_account(ctx.author)

        try:
            balance = await self.get_balance(ctx.author)
        except:
            balance = 0

        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute("SELECT SUM(balance) FROM economy")
                total = int((await db.fetchone())[0])

        em = discord.Embed(color=0xDEADBF,
                           title=getlang(lang)["eco"]["welcome"])
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.add_field(name=getlang(lang)["eco"]["total_amount"], value=str(total))
        em.add_field(name=getlang(lang)["eco"]["user_amount"], value=str(balance))
        em.add_field(name="owo", value=getlang(lang)["eco"]["footer"])

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def register(self, ctx):
        """Register a bank account"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if not await self.has_level_account(ctx.author):
            await self._levels_create_account(ctx.author)

        if not await self.has_account(ctx.author):
            await ctx.send(getlang(lang)["eco"]["registered"])
            await self._economy_create_account(ctx.author)
        else:
            await ctx.send(getlang(lang)["eco"]["already_registered"])

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def profile(self, ctx, user : discord.Member = None):
        """Get user's profile"""
        await ctx.trigger_typing()
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if user is None:
            user = ctx.author

        if not await self.has_level_account(user):
            await self._levels_create_account(user)

        if not await self.has_level_account(user):
            description = ""
        else:
            async with self.bot.sql_conn.acquire() as conn:
                async with conn.cursor() as db:
                    await db.execute("SELECT info FROM levels WHERE userid = %s", (user.id,))
                    description = (await db.fetchone())[0]

        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if not await db.execute("SELECT marryid FROM marriage WHERE userid = %s", (user.id)):
                    married = "Nobody"
                else:
                    married = await self.bot.get_user_info(int((await db.fetchone())[0]))

        if not await self.has_account(user):
            balance = 0
        else:
            balance = await self.get_balance(user)

        xp = await self.bot.redis.get(f"{ctx.message.author.id}-xp")
        if xp:
            xp = int(xp)
            level = self._find_level(xp)
            required = self._level_exp(level + 1)
        else:
            xp = 0
            level = 0
            required = 0

        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.weeb.sh/reputation/{self.bot.user.id}/{user.id}",
                               headers={"Authorization": "Wolke " + config.weeb}) as r:
                data = await r.json()
        embed = discord.Embed(color=0xDEABDF, title=getlang(lang)["eco"]["profile"]["title"].format(user.name),
                              description=getlang(lang)["eco"]["profile"]["description"].format(balance,
                                                                                          data['user']['reputation'],
                                                                                          level, xp, required,
                                                                                          description,
                                                                                          married))
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['payday'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def daily(self, ctx):
        """Receive your daily bonus"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        user = ctx.author

        if not await self.has_level_account(user):
            await self._levels_create_account(user)

        if not await self.has_account(user):
            await ctx.send(getlang(lang)["eco"]["no_account"])
            return
        else:
            async with self.bot.sql_conn.acquire() as conn:
                async with conn.cursor() as db:
                    await db.execute("SELECT payday FROM economy WHERE userid = %s", (user.id,))
                    paydaytime = int((await db.fetchone())[0])

            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(paydaytime).strftime("%d")
            if timecheck == timenow:
                tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1),
                                                     hour=0, minute=0, second=0)
                delta = tomorrow - datetime.datetime.now()
                timeleft = time.strftime("%H", time.gmtime(delta.seconds))
                await ctx.send(getlang(lang)["eco"]["daily_timer"].format(int(timeleft)))
                return
            else:
                balance = await self.get_balance(user)

                if await self.has_voted(user):
                    await self.edit_balance(user, balance + 7500)
                    await self.update_payday_time(user)
                    embed = discord.Embed(color=0xDEADBF,
                                          title=getlang(lang)["eco"]["daily_credits"],
                                          description=getlang(lang)["eco"]["daily_voter"])
                    await ctx.send(embed=embed)
                else:
                    await self.edit_balance(user, balance + 2500)
                    await self.update_payday_time(user)
                    embed = discord.Embed(color=0xDEADBF,
                                          title=getlang(lang)["eco"]["daily_credits"],
                                          description=getlang(lang)["eco"]["daily_normal"])
                    embed.set_footer(text=getlang(lang)["eco"]["vote_footer"])
                    await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rep(self, ctx, user : discord.Member):
        """Give user reputation"""
        await ctx.trigger_typing()
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        author = ctx.author
        if user == author:
            await ctx.send(getlang(lang)["eco"]["cant_rep_self"])
            return
        elif user.bot:
            await ctx.send(getlang(lang)["eco"]["cant_rep_bots"])
            return
        async with aiohttp.ClientSession() as cs:
            async with cs.post(f"https://api.weeb.sh/reputation/310039170792030211/{user.id}",
                               headers={"Authorization": "Wolke " + config.weeb},
                               data={"source_user": str(author.id)}) as r:
                data = await r.json()
            async with cs.get(f"https://api.weeb.sh/reputation/310039170792030211/{author.id}",
                               headers={"Authorization": "Wolke " + config.weeb}) as r:
                repdata = await r.json()

        availablerep = repdata['user']['availableReputations']
        if availablerep > 1:
            points = getlang(lang)["eco"]["points"]
        else:
            points = getlang(lang)["eco"]["point"]
        if data['status'] == 200:
            em = discord.Embed(color=0xDEADBF, title=getlang(lang)["eco"]["given_rep"],
                               description=getlang(lang)["eco"]["rep_msg"].format(author, user,
                                                                                  data['targetUser']['reputation'],
                                                                                  availablerep, points))
            return await ctx.send(embed=em)
        else:
            em = discord.Embed(color=0xDEADBF, title=getlang(lang)["eco"]["failed_rep"],
                               description=getlang(lang)["eco"]["no_rep_points"].format(author))
            return await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setdesc(self, ctx, *, desc : str):
        """Set profile description"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        user = ctx.author

        if not await self.has_level_account(user):
            await self._levels_create_account(user)

        if len(desc) > 500:
            await ctx.send(getlang(lang)["eco"]["set_desc"]["over_limit"])
            return
        else:
            try:
                async with self.bot.sql_conn.acquire() as conn:
                    async with conn.cursor() as db:
                        await db.execute("UPDATE levels SET info = %s WHERE userid = %s", (desc, ctx.author.id,))
                await ctx.send(getlang(lang)["eco"]["set_desc"]["updated"])
            except:
                await ctx.send(getlang(lang)["eco"]["set_desc"]["failed"])

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.guild_only()
    async def coinflip(self, ctx, amount:int):
        """Coinflip OwO"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        user = ctx.author

        if not await self.has_level_account(user):
            await self._levels_create_account(user)

        if amount <= 0:
            return await ctx.send(getlang(lang)["eco"]["coinflip"]["too_low"])
        elif amount > 100000:
            return await ctx.send(getlang(lang)["eco"]["coinflip"]["too_high"])

        if not await self.has_account(user):
            return await ctx.send(getlang(lang)["eco"]["no_account"])

        balance = await self.get_balance(user)

        if (balance - amount) < 0:
            await ctx.send(getlang(lang)["eco"]["coinflip"]["cant_spend"])
            log.info("%s (%s) tried to spend $%s on coinflip" % (ctx.author.name, ctx.author.id, amount,))
            return

        msg = await ctx.send(getlang(lang)["eco"]["coinflip"]["flipping"])
        await asyncio.sleep(random.randint(1, 5))

        choice = random.randint(0, 1)

        if choice == 1:
            em = discord.Embed(color=0x42FF73)
            em.description = getlang(lang)["eco"]["coinflip"]["won"].format(user, int(amount * .5))
            await msg.edit(embed=em, content=None)

            await self.edit_balance(user, balance + int(amount * .5))

            log.info("%s (%s) bet %s on coinflip and won %s" % (ctx.author.name,
                                                                ctx.author.id,
                                                                amount, int(amount * .5),))

        else:
            em = discord.Embed(color=0xFF5637, description=getlang(lang)["eco"]["coinflip"]["lost"])
            await msg.edit(embed=em, content=None)

            await self.edit_balance(user, balance - amount)

            log.info("%s (%s) bet %s on coinflip and lost" % (ctx.author.name, ctx.author.id, amount,))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def top(self, ctx):
        """Get Top Users OwO"""
        user = ctx.author
        if not await self.has_level_account(user):
            await self._levels_create_account(user)

        query = "SELECT userid, balance FROM economy ORDER BY balance+0 DESC LIMIT 10"

        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(query)
                allusers = await db.fetchall()

        table = PrettyTable()
        table.field_names = ["Username", "Balance"]

        for x in range(9):
            user = await self.bot.redis.get("ecotop%s" % int(x + 1))
            if not user:
                user = b"User not found."
            table.add_row([user.decode("utf8"), int(allusers[x][1])])

        await ctx.send(content=f"```\n{table}\n```", embed=None)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def transfer(self, ctx, user:discord.Member, amount:int,):
        """Transfer Credits to Users"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if not await self.has_level_account(ctx.author):
            await self._levels_create_account(ctx.author)

        if amount < 10:
            await ctx.send(getlang(lang)["eco"]["transfer"]["min"])
            return
        if user.bot:
            await ctx.send(getlang(lang)["eco"]["transfer"]["bot"])
            return
        elif user == ctx.message.author:
            await ctx.send(getlang(lang)["eco"]["transfer"]["self"])
            return
        else:
            if not await self.has_account(ctx.author):
                await ctx.send(getlang(lang)["eco"]["no_account"])
                return
            elif not await self.has_account(user):
                await ctx.send(getlang(lang)["eco"]["transfer"]["user_no_account"].format(user))
                return
            else:
                author_balance = await self.get_balance(ctx.author)
                user_balance = await self.get_balance(user)
                if (author_balance - amount) < 0:
                    await ctx.send(getlang(lang)["eco"]["coinflip"]["cant_spend"])
                    return
                else:
                    await self.edit_balance(user, user_balance + int(amount - (amount * .07)))
                    await self.edit_balance(ctx.author, author_balance - amount)
                    await ctx.send(getlang(lang)["eco"]["transfer"]["sent"].format(int(amount - (amount * .07)), user))
                    async with self.bot.sql_conn.acquire() as conn:
                        async with conn.cursor() as db:
                            await db.execute("SELECT balance FROM economy WHERE userid = 270133511325876224")
                            rektbal = int((await db.fetchone())[0])
                            await db.execute("UPDATE economy SET balance = %s WHERE userid = 270133511325876224",
                                             (rektbal + int(amount * .07),))
                    log.info("%s (%s) sent %s (%s) $%s" % (ctx.author.name, ctx.author.id,
                                                              user.name, user.id, amount,))
                    try:
                        await user.send(f"{ctx.author.name} has sent you ${amount}.")
                    except:
                        pass

    async def delmsg(self, msg:discord.Message):
        try:
            await msg.delete()
        except:
            pass

    @commands.command(aliases=['bj'])
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def blackjack(self, ctx, amount:int):
        """Blackjack"""
        author = ctx.author

        if not await self.has_level_account(author):
            await self._levels_create_account(author)

        if not await self.has_account(ctx.author):
            await ctx.send("You don't have a bank account...")
            return

        author_balance = await self.get_balance(ctx.author)

        if amount <= 0:
            await ctx.send("You can't bet that low...")
            return
        if (author_balance - amount) < 0:
            await ctx.send("You don't have that much to bet...")
            return
        if amount > 50000:
            await ctx.send("You can't bet past 50k")
            return

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

        while True:
            card = random.choice(cards)
            if card not in author_deck:
                author_deck.append(card)
                if card in special:
                    card = 10
                author_deck_n.append(card)
            if len(author_deck) == 5:
                break

        while True:
            card = random.choice(cards)
            if card not in bot_deck:
                bot_deck.append(card)
                if card in special:
                    card = 10
                bot_deck_n.append(card)
            if len(bot_deck) == 5:
                break

        win_embed = discord.Embed(color=0xDEADBF)
        win_embed.title = "Blackjack Win"
        win_embed.description = "**%s** (%s) has won %s" % (ctx.author.name, ctx.author.id, int(amount * .5))

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
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.edit_balance(ctx.author, author_balance + int(amount * .5))
            else:
                em.description = "I beat you >:3"
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.edit_balance(ctx.author, author_balance - amount)
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
                await self.edit_balance(ctx.author, author_balance - amount)
            else:
                em.description = "I went over 21 and you won ;w;"
                await self.edit_balance(ctx.author, author_balance + int(amount * .5))

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
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.edit_balance(ctx.author, author_balance + int(amount * .5))
            else:
                em.description = "I beat you >:3"
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.edit_balance(ctx.author, author_balance - amount)
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
                await self.edit_balance(ctx.author, author_balance - amount)
            else:
                em.description = "I went over 21 and you won ;w;"
                await self.edit_balance(ctx.author, author_balance + int(amount * .5))

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
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.edit_balance(ctx.author, author_balance + int(amount * .5))
            else:
                em.description = "I beat you >:3"
                em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
                em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
                await self.edit_balance(ctx.author, author_balance - amount)
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
                await self.edit_balance(ctx.author, author_balance - amount)
            else:
                em.description = "I went over 21 and you won ;w;"
                await self.edit_balance(ctx.author, author_balance + int(amount * .5))

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
            await self.edit_balance(ctx.author, author_balance + int(amount * .5))
        else:
            em.description = "I beat you >:3"
            await self.edit_balance(ctx.author, author_balance - amount)

        em.add_field(name="Your Cards (%s)" % author_total, value=author_value, inline=True)
        em.add_field(name="My Cards (%s)" % bot_total, value=bot_value, inline=True)
        return await msg.edit(embed=em)

    async def on_message(self, message):
        if random.randint(1, 30) == 1:
            if not await self.bot.redis.get(f"{message.author.id}-xp"):
                await self.bot.redis.set(f"{message.author.id}-xp", 0)
            currxp = await self.bot.redis.get(f"{message.author.id}-xp")
            currxp = int(currxp)
            newxp = random.randint(1, 10)
            await self.bot.redis.set(f"{message.author.id}-xp", currxp + newxp)

def setup(bot):
    n = economy(bot)
    bot.add_cog(n)