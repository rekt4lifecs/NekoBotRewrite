from discord.ext import commands
import discord, aiohttp, asyncio, datetime, config, random, math, logging
import time
import ujson
from prettytable import PrettyTable

log = logging.getLogger("NekoBot")

# Languages
languages = ["english", "weeb", "tsundere"]
lang = {}

for l in languages:
    with open("lang/%s.json" % l) as f:
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
    @commands.cooldown(1, 120, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def coinflip(self, ctx, amount : int):
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
            await ctx.send(getlang(lang)["eco"]["coinflip"]["too_low"])
            return
        elif amount > 100000:
            await ctx.send(getlang(lang)["eco"]["coinflip"]["too_high"])
            return
        if not await self.has_account(user):
            await ctx.send(getlang(lang)["eco"]["no_account"])
            return
        else:
            balance = await self.get_balance(user)
            if (balance - amount) < 0:
                await ctx.send(getlang(lang)["eco"]["coinflip"]["cant_spend"])
                return
            else:
                msg = await ctx.send(getlang(lang)["eco"]["coinflip"]["flipping"])
                await asyncio.sleep(random.randint(1, 5))
                await self.edit_balance(user, balance - amount)
                choice = random.randint(0, 1)
                if choice == 1:
                    try:
                        await ctx.message.add_reaction('🎉')
                    except:
                        pass
                    em = discord.Embed(color=0x42FF73)
                    em.description = getlang(lang)["eco"]["coinflip"]["won"].format(user, amount * 1.5)
                    await msg.edit(embed=em, content=None)
                    await self.edit_balance(user, balance + int(amount * 1.5))
                else:
                    em = discord.Embed(color=0xFF5637, description=getlang(lang)["eco"]["coinflip"]["lost"])
                    await msg.edit(embed=em, content=None)
                    try:
                        await ctx.message.add_reaction('😦')
                    except:
                        pass

    @commands.command()
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def transfer(self, ctx, amount : int, user : discord.Member):
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
                    await self.edit_balance(user, user_balance + amount)
                    await self.edit_balance(ctx.author, author_balance - amount)
                    await ctx.send(getlang(lang)["eco"]["transfer"]["sent"].format(amount, user))
                    try:
                        await user.send(f"{ctx.author.name} has sent you ${amount}.")
                    except:
                        pass

    # @commands.command(aliases=['bj'])
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def blackjack(self, ctx, betting_amount: int):
    #     if not await self.has_level_account(ctx.author):
    #         await self._levels_create_account(ctx.author)
    #     cards = {
    #         "2C": "<:2C:424587135463456778>",
    #         "2D": "<:2D:424587135383764993>",
    #         "2H": "<:2H:424587135346147329>",
    #         "2S": "<:2S:424587135341821954>",
    #         "3C": "<:3C:424587163737522176>",
    #         "3D": "<:3D:424587162437156874>",
    #         "3H": "<:3H:424587162579763202>",
    #         "3S": "<:3S:424587163745779712>",
    #         "4C": "<:4C:424587171232743425>",
    #         "4D": "<:4D:424587163737391104>",
    #         "4H": "<:4H:424587169865138176>",
    #         "4S": "<:4S:424587170028978186>",
    #         "5C": "<:5C:424587178933223425>",
    #         "5D": "<:5D:424587173111529482>",
    #         "5H": "<:5H:424587174348980225>",
    #         "5S": "<:5S:424587172994088970>",
    #         "6C": "<:6C:424587180938231808>",
    #         "6D": "<:6D:424587177717137419>",
    #         "6H": "<:6H:424587178392158208>",
    #         "6S": "<:6S:424587177360621586>",
    #         "7C": "<:7C:424587184650059779>",
    #         "7D": "<:7D:424587179134681090>",
    #         "7H": "<:7H:424587179109515266>",
    #         "7S": "<:7S:424587177565880331>",
    #         "8C": "<:8C:424587186160271400>",
    #         "8D": "<:8D:424587181970161667>",
    #         "8H": "<:8H:424587182377009152>",
    #         "8S": "<:8S:424587182330871808>",
    #         "9C": "<:9C:424587184717168640>",
    #         "9D": "<:9D:424587183035252757>",
    #         "9H": "<:9H:424587181978419221>",
    #         "9S": "<:9S:424587182146191362>",
    #         "10C": "<:10C:424587186055151617>",
    #         "10D": "<:10D:424587182234140672>",
    #         "10H": "<:10H:424587182360100874>",
    #         "10S": "<:10S:424587182070693889>",
    #         "AC": "<:AC:424587167864717313>",
    #         "AD": "<:AD:424587167965118465>",
    #         "AH": "<:AH:424587168183222272>",
    #         "AS": "<:AS:424587182297317376>",
    #         "KC": "<:KC:424587233182351362>",
    #         "KD": "<:KD:424587236651171840>",
    #         "KH": "<:KH:424587237968314370>",
    #         "KS": "<:KS:424587238068715541>",
    #         "QC": "<:QC:424587235715973130>",
    #         "QD": "<:QD:424587237943148555>",
    #         "QH": "<:QH:424587080824389653>",
    #         "QS": "<:QS:424587085538787348>",
    #         "JC": "<:JC:424587235673767966>",
    #         "JD": "<:JD:424587237590827018>",
    #         "JH": "<:JH:424587239419281431>",
    #         "JS": "<:JS:424587238308052992>",
    #     }
    #     lst = []
    #     for card in cards:
    #         lst.append(card)
    #
    #     author = ctx.message.author
    #
    #     if not await self.has_account(ctx.author):
    #         await ctx.send("You don't have a bank account...")
    #         return
    #
    #     author_balance = await self.get_balance(ctx.author)
    #
    #     if betting_amount <= 0:
    #         await ctx.send("You can't bet that low...")
    #         return
    #     if (author_balance - betting_amount) < 0:
    #         await ctx.send("You don't have that much to bet...")
    #         return
    #     if betting_amount > 50000:
    #         await ctx.send("You can't bet past 50k")
    #         return
    #
    #     win_embed = discord.Embed(color=0xDEADBF)
    #     win_embed.title = "Blackjack Win"
    #     win_embed.description = "**%s** (%s) has won %s" % (ctx.author.name, ctx.author.id, int(betting_amount * 1.5))
    #
    #     lose_embed = discord.Embed(color=0xDEADBF)
    #     lose_embed.title = "Blackjack Lose"
    #     lose_embed.description = "**%s** (%s) has lost %s" % (ctx.author.name, ctx.author.id, int(betting_amount))
    #
    #     # Take users moneylol
    #     await self.edit_balance(ctx.author, author_balance - betting_amount)
    #
    #     # Get New Author Balance
    #     author_balance = await self.get_balance(ctx.author)
    #
    #     card_choice1 = cards[random.choice(lst)]
    #     card_choice2 = cards[random.choice(lst)]
    #
    #     bot_choice1 = cards[random.choice(lst)]
    #     bot_choice2 = cards[random.choice(lst)]
    #
    #     amount1 = card_choice1[2]
    #     amount2 = card_choice2[2]
    #     amount3 = bot_choice1[2]
    #     amount4 = bot_choice2[2]
    #
    #     if amount1 is "Q" or amount1 is "K" or amount1 is "J":
    #         amount1 = 10
    #     if amount2 is "Q" or amount2 is "K" or amount2 is "J":
    #         amount2 = 10
    #     if amount3 is "Q" or amount3 is "K" or amount3 is "J":
    #         amount3 = 10
    #     if amount4 is "Q" or amount4 is "K" or amount4 is "J":
    #         amount4 = 10
    #
    #     if amount1 is "A":
    #         amount1 = 11
    #     if amount2 is "A":
    #         amount2 = 11
    #     if amount3 is "A":
    #         amount3 = 11
    #     if amount4 is "A":
    #         amount4 = 11
    #
    #     e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
    #     e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2)}", value=f"{amount1}{card_choice1}| {amount2}{card_choice2}", inline=True)
    #     e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ?", inline=True)
    #
    #     msg = await ctx.send(embed=e)
    #
    #     def check(m):
    #         return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author
    #
    #     try:
    #         await self.bot.wait_for('message', check=check, timeout=7.5)
    #     except:
    #         if (int(amount1) + int(amount2)) > (int(amount3) + int(amount4)):
    #             winner = author.name
    #             color = 0xDEADBF
    #             await self.post_to_transactions(win_embed)
    #             await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #         else:
    #             winner = self.bot.user.name
    #             await self.post_to_transactions(lose_embed)
    #             color = 0xff5630
    #         await msg.edit(embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
    #         await self.post_to_transactions(win_embed)
    #         return
    #
    #     # 2nd screen #
    #
    #     card_choice3 = cards[random.choice(lst)]
    #
    #     bot_choice3 = cards[random.choice(lst)]
    #
    #     amount5 = card_choice3[2]
    #     amount6 = bot_choice3[2]
    #
    #     if amount5 is "Q" or amount5 is "K" or amount5 is "J":
    #         amount5 = 10
    #     if amount6 is "Q" or amount6 is "K" or amount6 is "J":
    #         amount6 = 10
    #
    #     if amount5 is "A":
    #         amount5 = 11
    #     if amount6 is "A":
    #         amount6 = 11
    #
    #     if (int(amount1) + int(amount2) + int(amount5)) > 21:
    #         e = discord.Embed(color=0xff5630, title="Blackjack", description=f"{author.name} went over 21 and {self.bot.user.name} won!")
    #         e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
    #                     value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}",
    #                     inline=True)
    #         e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
    #                     value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount5}{bot_choice3}",
    #                     inline=True)
    #         await self.post_to_transactions(lose_embed)
    #         await msg.edit(embed=e)
    #         return
    #     elif (int(amount3) + int(amount4) + int(amount6)) > 21:
    #         await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #         e = discord.Embed(color=0xff5630, title="Blackjack",
    #                           description=f"{self.bot.user.name} went over 21 and {author.name} won!")
    #         e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
    #                     value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}",
    #                     inline=True)
    #         e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
    #                     value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount6}{bot_choice3}",
    #                     inline=True)
    #         await self.post_to_transactions(win_embed)
    #         await msg.edit(embed=e)
    #         return
    #
    #     e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
    #     e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
    #                 value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}|{card_choice3}", inline=True)
    #     e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ? | ?", inline=True)
    #
    #     msg = await ctx.send(embed=e)
    #
    #     def check(m):
    #         return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author
    #
    #     try:
    #         await self.bot.wait_for('message', check=check, timeout=7.5)
    #     except:
    #         if (int(amount1) + int(amount2) + int(amount5)) > (int(amount3) + int(amount4) + int(amount6)):
    #             winner = author.name
    #             color = 0xDEADBF
    #             await self.post_to_transactions(win_embed)
    #             await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #         else:
    #             winner = self.bot.user.name
    #             await self.post_to_transactions(lose_embed)
    #             color = 0xff5630
    #         await msg.edit(
    #             embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
    #         return
    #
    #     # 3rd screen #
    #
    #     card_choice4 = cards[random.choice(lst)]
    #
    #     bot_choice4 = cards[random.choice(lst)]
    #
    #     amount7 = card_choice3[2]
    #     amount8 = bot_choice3[2]
    #
    #     if amount7 is "Q" or amount7 is "K" or amount7 is "J":
    #         amount7 = 10
    #     if amount8 is "Q" or amount8 is "K" or amount8 is "J":
    #         amount8 = 10
    #
    #     if amount7 is "A":
    #         amount7 = 11
    #     if amount8 is "A":
    #         amount8 = 11
    #
    #     if (int(amount1) + int(amount2) + int(amount5) + int(amount7)) > 21:
    #         e = discord.Embed(color=0xff5630, title="Blackjack",
    #                           description=f"{author.name} went over 21 and {self.bot.user.name} won!")
    #         e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
    #                     value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}",
    #                     inline=True)
    #         e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
    #                     value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount5}{bot_choice3}",
    #                     inline=True)
    #         await self.post_to_transactions(lose_embed)
    #         await msg.edit(embed=e)
    #         return
    #     elif (int(amount3) + int(amount4) + int(amount6) + int(amount8)) > 21:
    #         await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #         e = discord.Embed(color=0xff5630, title="Blackjack",
    #                           description=f"{self.bot.user.name} went over 21 and {author.name} won!")
    #         e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
    #                     value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}| {amount7}{card_choice4}",
    #                     inline=True)
    #         e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
    #                     value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount6}{bot_choice3}| {amount8}{bot_choice4}",
    #                     inline=True)
    #         await self.post_to_transactions(win_embed)
    #         await msg.edit(embed=e)
    #         return
    #
    #     e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
    #     e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount7)}",
    #                 value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}|{card_choice3}| {amount7}{card_choice4}", inline=True)
    #     e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ? | ? | ?", inline=True)
    #
    #     msg = await ctx.send(embed=e)
    #
    #     def check(m):
    #         return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author
    #
    #     try:
    #         await self.bot.wait_for('message', check=check, timeout=7.5)
    #     except:
    #         if (int(amount1) + int(amount2) + int(amount5) + int(amount7)) > (int(amount3) + int(amount4) + int(amount6) + int(amount8)):
    #             winner = author.name
    #             color = 0xDEADBF
    #             await self.post_to_transactions(win_embed)
    #             await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #         else:
    #             winner = self.bot.user.name
    #             await self.post_to_transactions(lose_embed)
    #             color = 0xff5630
    #         await msg.edit(
    #             embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
    #         return
    #
    #     # 3rd screen #
    #
    #     card_choice5 = cards[random.choice(lst)]
    #
    #     bot_choice5 = cards[random.choice(lst)]
    #
    #     amount9 = card_choice3[2]
    #     amount10 = bot_choice3[2]
    #
    #     if amount9 is "Q" or amount9 is "K" or amount9 is "J":
    #         amount9 = 10
    #     if amount10 is "Q" or amount10 is "K" or amount10 is "J":
    #         amount10 = 10
    #
    #     if amount9 is "A":
    #         amount9 = 11
    #     if amount10 is "A":
    #         amount10 = 11
    #
    #     if (int(amount1) + int(amount2) + int(amount5) + int(amount9) + int(amount7)) > 21:
    #         e = discord.Embed(color=0xff5630, title="Blackjack",
    #                           description=f"{author.name} went over 21 and {self.bot.user.name} won!")
    #         e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount7)}",
    #                     value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}| {amount7}{card_choice5}",
    #                     inline=True)
    #         e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6) + int(amount8) + int(amount10)}",
    #                     value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount5}{bot_choice3}| {amount10}{bot_choice3}",
    #                     inline=True)
    #         await self.post_to_transactions(lose_embed)
    #         await msg.edit(embed=e)
    #         return
    #     elif (int(amount3) + int(amount4) + int(amount6) + int(amount10) + int(amount8)) > 21:
    #         await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #         e = discord.Embed(color=0xff5630, title="Blackjack",
    #                           description=f"{self.bot.user.name} went over 21 and {author.name} won!")
    #         e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount7) + int(amount9)}",
    #                     value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}| {amount9}{card_choice5}| {amount7}|{card_choice4}",
    #                     inline=True)
    #         e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
    #                     value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount6}{bot_choice3}| {amount10}{bot_choice5}| {amount8}{bot_choice4}",
    #                     inline=True)
    #         await self.post_to_transactions(win_embed)
    #         await msg.edit(embed=e)
    #         return
    #
    #     e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
    #     e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount9) + int(amount7)}",
    #                 value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}|{card_choice3}| {amount7}{card_choice4}| {amount9}{card_choice5}", inline=True)
    #     e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ? | ? | ? | ?", inline=True)
    #
    #     msg = await ctx.send(embed=e)
    #
    #     def check(m):
    #         return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author
    #
    #     try:
    #         await self.bot.wait_for('message', check=check, timeout=7.5)
    #     except:
    #         if (int(amount1) + int(amount2) + int(amount5) + int(amount7) + int(amount9)) > (int(amount3) + int(amount4) + int(amount6) + int(amount8) + int(amount10)):
    #             winner = author.name
    #             await self.post_to_transactions(win_embed)
    #             color = 0xDEADBF
    #             await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #         else:
    #             winner = self.bot.user.name
    #             await self.post_to_transactions(lose_embed)
    #             color = 0xff5630
    #         await msg.edit(
    #             embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
    #         return
    #
    #     if (int(amount1) + int(amount2) + int(amount5) + int(amount7) + int(amount9)) > (
    #             int(amount3) + int(amount4) + int(amount6) + int(amount8) + int(amount10)):
    #         winner = author.name
    #         await self.post_to_transactions(win_embed)
    #         color = 0xDEADBF
    #         await self.edit_balance(ctx.author, author_balance + int(betting_amount * 1.5))
    #     else:
    #         winner = self.bot.user.name
    #         await self.post_to_transactions(lose_embed)
    #         color = 0xff5630
    #     await msg.edit(
    #         embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))

    async def delmsg(self, msg:discord.Message):
        try:
            await msg.delete()
        except:
            pass

    @commands.command(aliases=['bj'])
    @commands.guild_only()
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

        await self.edit_balance(ctx.author, author_balance - amount)

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
        win_embed.description = "**%s** (%s) has won %s" % (ctx.author.name, ctx.author.id, int(amount * 1.5))

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
                await self.edit_balance(ctx.author, author_balance + int(amount * 1.5))
            else:
                em.description = "I beat you >:3"
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
            else:
                em.description = "I went over 21 and you won ;w;"
                await self.edit_balance(ctx.author, author_balance + int(amount * 1.5))

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
                await self.edit_balance(ctx.author, author_balance + int(amount * 1.5))
            else:
                em.description = "I beat you >:3"
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
            else:
                em.description = "I went over 21 and you won ;w;"
                await self.edit_balance(ctx.author, author_balance + int(amount * 1.5))

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
                await self.edit_balance(ctx.author, author_balance + int(amount * 1.5))
            else:
                em.description = "I beat you >:3"
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
            else:
                em.description = "I went over 21 and you won ;w;"
                await self.edit_balance(ctx.author, author_balance + int(amount * 1.5))

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
            await self.edit_balance(ctx.author, author_balance + int(amount * 1.5))
        else:
            em.description = "I beat you >:3"

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