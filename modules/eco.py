from discord.ext import commands
import discord, aiohttp, asyncio, time, datetime, config, random, math, logging
import aiomysql
import ujson
import string
from prettytable import PrettyTable

log = logging.getLogger("NekoBot")

# Languages
languages = ["english", "weeb", "tsundere"]
l = {}

for l in languages:
    with open("lang/%s.json" % l) as f:
        lang[l] = ujson.load(f)

def getlang(lang:str):
    return lang.get(lang, None)

class economy:
    """Economy"""

    def __init__(self, bot):
        self.bot = bot

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

    def forbiddencheck(self, text:str):
        characters = string.ascii_letters + string.digits + " "
        forbidden_char = 0
        for letter in text:
            if letter not in characters:
                forbidden_char += 1
        return forbidden_char

    async def usercheck(self, datab : str, user : discord.Member):
        user = user.id
        if not await self.execute(query=f'SELECT 1 FROM {datab} WHERE userid = {user}', isSelect=True):
            return False
        else:
            return True

    def _required_exp(self, level: int):
        if level < 0:
            return 0
        return 139 * level + 65

    def _level_exp(self, level: int):
        return level * 65 + 139 * level * (level - 1) // 2

    def _find_level(self, total_exp):
        return int((1 / 278) * (9 + math.sqrt(81 + 1112 * (total_exp))))

    async def _create_user(self, user_id):
        try:
            await self.execute(f"INSERT INTO levels VALUES ({user_id}, 0, 0, 0, 0, 0, 0)", commit=True)
        except:
            pass

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bank(self, ctx):
        """Bank info"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        try:
            x = await self.execute(f"SELECT balance FROM economy WHERE userid = {ctx.message.author.id}", isSelect=True)
            balance = int(x[0])
        except:
            balance = 0
        total = 0
        all_eco = await self.execute("SELECT balance FROM economy", isSelect=True, fetchAll=True)
        for x in all_eco:
            total = total + int(x[0])

        em = discord.Embed(color=0xDEADBF,
                           title=getlang(lang)["eco"]["welcome"])
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.add_field(name=getlang(lang)["eco"]["total_amount"], value=f"{total}")
        em.add_field(name=getlang(lang)["eco"]["user_amount"], value=balance)
        em.add_field(name="owo", value=getlang(lang)["eco"]["footer"])

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def register(self, ctx):
        """Register a bank account"""
        user = ctx.message.author
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass

        if await self.usercheck('economy', user) is False:
            await ctx.send(getlang(lang)["eco"]["registered"])
            await self.execute(f"INSERT INTO economy VALUES ({user.id}, 0, 0)", commit=True)
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

        if user == None:
            user = ctx.message.author
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        username = str(user.name)
        if await self.usercheck('levels', user) is False:
            level = 0
            xp = 0
            required = 0
            description = ""
        else:
            fetchlvl = await self.execute(f"SELECT rep, level, info FROM levels WHERE userid = {user.id}", isSelect=True, fetchAll=True)
            xp = fetchlvl[0][1]
            description = fetchlvl[0][2]
            level = self._find_level(xp)
            required = self._level_exp(level + 1)
        if await self.usercheck('marriage', user) is False:
            married = "Nobody"
        else:
            x = await self.execute(f"SELECT marryid FROM marriage WHERE userid = {user.id}", isSelect=True)
            marryid = int(x[0])
            married = await self.bot.get_user_info(marryid)
        if await self.usercheck('economy', user):
            x = await self.execute(f"SELECT balance FROM economy WHERE userid = {user.id}", isSelect=True)
            balance = int(x[0])
        else:
            balance = 0
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
        embed = discord.Embed(color=0xDEABDF, title=getlang(lang)["eco"]["profile"]["title"].format(username),
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

        user = ctx.message.author
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        if await self.usercheck('economy', user) is False:
            await ctx.send(getlang(lang)["eco"]["no_account"])
            return
        else:
            x = await self.execute(f"SELECT payday FROM economy WHERE userid = {user.id}", isSelect=True)
            paydaytime = x[0]
            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(int(paydaytime)).strftime("%d")
            if timecheck == timenow:
                tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1),
                                                     hour=0, minute=0, second=0)
                delta = tomorrow - datetime.datetime.now()
                timeleft = time.strftime("%H", time.gmtime(delta.seconds))
                await ctx.send(getlang(lang)["eco"]["daily_timer"].format(int(timeleft)))
                return
            else:
                x = await self.execute(f"SELECT balance FROM economy WHERE userid = {user.id}", isSelect=True)
                balance = int(x[0])

                # Voter Bonus
                amount = await self.execute(f'SELECT 1 FROM dbl WHERE user = {ctx.message.author.id} AND type = \"upvote\"', isSelect=True)
                if amount != 0:
                    await self.execute(f"UPDATE economy SET balance = {balance + 7500} WHERE userid = {user.id}", commit=True)
                    await self.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}", commit=True)
                    embed = discord.Embed(color=0xDEADBF,
                                          title=getlang(lang)["eco"]["daily_credits"],
                                          description=getlang(lang)["eco"]["daily_voter"])
                    await ctx.send(embed=embed)
                else:
                    await self.execute(f"UPDATE economy SET balance = {balance + 2500} WHERE userid = {user.id}", commit=True)
                    await self.execute(f"UPDATE economy SET payday = {int(time.time())} WHERE userid = {user.id}", commit=True)
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
        author = ctx.message.author
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
        # await ctx.send(f"```\n{json.dumps(data, indent=4)}\n```")
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
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        if await self.usercheck("levels", ctx.message.author) is False:
            await ctx.send("Error finding your profile.")
            return
        if self.forbiddencheck(str(desc)) >= 1:
            return await ctx.send("**Text has forbidden characters.**")
        if len(desc) > 500:
            await ctx.send(getlang(lang)["eco"]["set_desc"]["over_limit"])
            return
        else:
            try:
                await self.execute(f"UPDATE levels SET info = \"{desc}\" WHERE userid = {ctx.message.author.id}", commit=True)
                await ctx.send(getlang(lang)["eco"]["set_desc"]["updated"])
            except:
                await ctx.send(getlang(lang)["eco"]["set_desc"]["failed"])

    @commands.command(aliases=['del'], hidden=True)
    @commands.is_owner()
    async def poof(self, ctx, _id : int):
        await self.execute(f"DELETE FROM levels WHERE userid = {_id}", commit=True)
        ctx.send(f"Deleted {_id}")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def coinflip(self, ctx, amount : int):
        """Coinflip OwO"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        user = ctx.message.author
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        if amount <= 0:
            await ctx.send(getlang(lang)["eco"]["coinflip"]["too_low"])
            return
        elif amount > 10000:
            await ctx.send(getlang(lang)["eco"]["coinflip"]["too_high"])
            return
        if await self.usercheck('economy', user) is False:
            await ctx.send(getlang(lang)["eco"]["no_account"])
            return
        else:
            x = await self.execute(f"SELECT balance FROM economy WHERE userid = {user.id}", isSelect=True)
            balance = int(x[0])
            if (balance - amount) < 0:
                await ctx.send(getlang(lang)["eco"]["coinflip"]["cant_spend"])
                return
            else:
                msg = await ctx.send(getlang(lang)["eco"]["coinflip"]["flipping"])
                await asyncio.sleep(random.randint(2, 5))
                await self.execute(f"UPDATE economy SET balance = {balance - amount} WHERE userid = {user.id}", commit=True)
                choice = random.randint(0, 1)
                if choice == 1:
                    try:
                        await ctx.message.add_reaction('🎉')
                    except:
                        pass
                    em = discord.Embed(color=0x42FF73, description=getlang(lang)["eco"]["coinflip"]["won"].format(user, amount * 1.5))
                    await msg.edit(embed=em)
                    await self.execute(f"UPDATE economy SET balance = {balance + int(amount * 1.5)} WHERE userid = {user.id}", commit=True)
                else:
                    em = discord.Embed(color=0xFF5637, description=getlang(lang)["eco"]["coinflip"]["lost"])
                    await msg.edit(embed=em)
                    try:
                        await ctx.message.add_reaction('😦')
                    except:
                        pass

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def top(self, ctx):
        """Get Top Users OwO"""
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        em = discord.Embed(color=0xDEADBF, title="Top Users | Economy", description="Loading...")
        msg = await ctx.send(embed=em)
        query = "SELECT userid, balance FROM economy ORDER BY balance+0 DESC LIMIT 10"
        allusers = await self.execute(query=query, isSelect=True, fetchAll=True)
        users = await self.execute("SELECT * FROM ecotop", isSelect=True)

        table = PrettyTable()
        table.field_names = ["Username", "Balance"]

        table.add_row([users[0], int(allusers[0][1])])
        table.add_row([users[1], int(allusers[1][1])])
        table.add_row([users[2], int(allusers[2][1])])
        table.add_row([users[3], int(allusers[3][1])])
        table.add_row([users[4], int(allusers[4][1])])
        table.add_row([users[5], int(allusers[5][1])])
        table.add_row([users[6], int(allusers[6][1])])
        table.add_row([users[7], int(allusers[7][1])])
        table.add_row([users[8], int(allusers[8][1])])
        table.add_row([users[9], int(allusers[9][1])])

        await msg.edit(content=f"```\n{table}\n```", embed=None)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def transfer(self, ctx, amount : int, user : discord.Member):
        """Transfer Credits to Users"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
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
            if await self.usercheck('economy', ctx.message.author) is False:
                await ctx.send(getlang(lang)["eco"]["no_account"])
                return
            elif await self.usercheck('economy', user) is False:
                await ctx.send(getlang(lang)["eco"]["transfer"]["user_no_account"].format(user))
                return
            else:
                x = await self.execute(f"SELECT balance FROM economy WHERE userid = {ctx.message.author.id}", isSelect=True)
                author_balance = int(x[0])
                x = await self.execute(f"SELECT balance FROM economy WHERE userid = {user.id}", isSelect=True)
                user_balance = int(x[0])
                if (author_balance - amount) < 0:
                    await ctx.send(getlang(lang)["eco"]["coinflip"]["cant_spend"])
                    return
                else:
                    await self.execute(f"UPDATE economy SET balance = {amount + user_balance} WHERE userid = {user.id}", commit=True)
                    await self.execute(f"UPDATE economy SET balance = {author_balance - amount} WHERE userid = {ctx.message.author.id}", commit=True)
                    await ctx.send(getlang(lang)["eco"]["transfer"]["sent"].format(amount, user))
                    try:
                        await user.send(f"{ctx.message.author.name} has sent you ${amount}.")
                    except:
                        pass

    @commands.command(aliases=['bj'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def blackjack(self, ctx, betting_amount: int):
        try:
            if await self.usercheck('levels', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        cards = {
            "2C": "<:2C:424587135463456778>",
            "2D": "<:2D:424587135383764993>",
            "2H": "<:2H:424587135346147329>",
            "2S": "<:2S:424587135341821954>",
            "3C": "<:3C:424587163737522176>",
            "3D": "<:3D:424587162437156874>",
            "3H": "<:3H:424587162579763202>",
            "3S": "<:3S:424587163745779712>",
            "4C": "<:4C:424587171232743425>",
            "4D": "<:4D:424587163737391104>",
            "4H": "<:4H:424587169865138176>",
            "4S": "<:4S:424587170028978186>",
            "5C": "<:5C:424587178933223425>",
            "5D": "<:5D:424587173111529482>",
            "5H": "<:5H:424587174348980225>",
            "5S": "<:5S:424587172994088970>",
            "6C": "<:6C:424587180938231808>",
            "6D": "<:6D:424587177717137419>",
            "6H": "<:6H:424587178392158208>",
            "6S": "<:6S:424587177360621586>",
            "7C": "<:7C:424587184650059779>",
            "7D": "<:7D:424587179134681090>",
            "7H": "<:7H:424587179109515266>",
            "7S": "<:7S:424587177565880331>",
            "8C": "<:8C:424587186160271400>",
            "8D": "<:8D:424587181970161667>",
            "8H": "<:8H:424587182377009152>",
            "8S": "<:8S:424587182330871808>",
            "9C": "<:9C:424587184717168640>",
            "9D": "<:9D:424587183035252757>",
            "9H": "<:9H:424587181978419221>",
            "9S": "<:9S:424587182146191362>",
            "10C": "<:10C:424587186055151617>",
            "10D": "<:10D:424587182234140672>",
            "10H": "<:10H:424587182360100874>",
            "10S": "<:10S:424587182070693889>",
            "AC": "<:AC:424587167864717313>",
            "AD": "<:AD:424587167965118465>",
            "AH": "<:AH:424587168183222272>",
            "AS": "<:AS:424587182297317376>",
            "KC": "<:KC:424587233182351362>",
            "KD": "<:KD:424587236651171840>",
            "KH": "<:KH:424587237968314370>",
            "KS": "<:KS:424587238068715541>",
            "QC": "<:QC:424587235715973130>",
            "QD": "<:QD:424587237943148555>",
            "QH": "<:QH:424587080824389653>",
            "QS": "<:QS:424587085538787348>",
            "JC": "<:JC:424587235673767966>",
            "JD": "<:JD:424587237590827018>",
            "JH": "<:JH:424587239419281431>",
            "JS": "<:JS:424587238308052992>",
        }
        lst = []
        for card in cards:
            lst.append(card)

        author = ctx.message.author

        if await self.usercheck('economy', author) is False:
            await ctx.send("You don't have a bank account...")
            return

        author_balance = await self.execute(f"SELECT balance FROM economy WHERE userid = {author.id}", isSelect=True)
        author_balance = int(author_balance[0])

        if betting_amount <= 0:
            await ctx.send("You can't bet that low...")
            return
        if (author_balance - betting_amount) < 0:
            await ctx.send("You don't have that much to bet...")
            return
        if betting_amount > 50000:
            await ctx.send("You can't bet past 50k")
            return

        # Take users moneylol
        await self.execute(f"UPDATE economy SET balance = {author_balance - betting_amount} WHERE userid = {author.id}",
                           commit=True)

        # Get New Author Balance
        author_balance = await self.execute(f"SELECT balance FROM economy WHERE userid = {author.id}", isSelect=True)
        author_balance = int(author_balance[0])

        card_choice1 = cards[random.choice(lst)]
        card_choice2 = cards[random.choice(lst)]

        bot_choice1 = cards[random.choice(lst)]
        bot_choice2 = cards[random.choice(lst)]

        amount1 = card_choice1[2]
        amount2 = card_choice2[2]
        amount3 = bot_choice1[2]
        amount4 = bot_choice2[2]

        if amount1 is "Q" or amount1 is "K" or amount1 is "J":
            amount1 = 10
        if amount2 is "Q" or amount2 is "K" or amount2 is "J":
            amount2 = 10
        if amount3 is "Q" or amount3 is "K" or amount3 is "J":
            amount3 = 10
        if amount4 is "Q" or amount4 is "K" or amount4 is "J":
            amount4 = 10

        if amount1 is "A":
            amount1 = 11
        if amount2 is "A":
            amount2 = 11
        if amount3 is "A":
            amount3 = 11
        if amount4 is "A":
            amount4 = 11

        e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
        e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2)}", value=f"{amount1}{card_choice1}| {amount2}{card_choice2}", inline=True)
        e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ?", inline=True)

        msg = await ctx.send(embed=e)

        def check(m):
            return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author

        try:
            await self.bot.wait_for('message', check=check, timeout=7.5)
        except:
            if (int(amount1) + int(amount2)) > (int(amount3) + int(amount4)):
                winner = author.name
                color = 0xDEADBF
                await self.execute(f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}", commit=True)
            else:
                winner = self.bot.user.name
                color = 0xff5630
            await msg.edit(embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
            return

        # 2nd screen #

        card_choice3 = cards[random.choice(lst)]

        bot_choice3 = cards[random.choice(lst)]

        amount5 = card_choice3[2]
        amount6 = bot_choice3[2]

        if amount5 is "Q" or amount5 is "K" or amount5 is "J":
            amount5 = 10
        if amount6 is "Q" or amount6 is "K" or amount6 is "J":
            amount6 = 10

        if amount5 is "A":
            amount5 = 11
        if amount6 is "A":
            amount6 = 11

        if (int(amount1) + int(amount2) + int(amount5)) > 21:
            e = discord.Embed(color=0xff5630, title="Blackjack", description=f"{author.name} went over 21 and {self.bot.user.name} won!")
            e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
                        value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}",
                        inline=True)
            e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
                        value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount5}{bot_choice3}",
                        inline=True)
            await msg.edit(embed=e)
            return
        elif (int(amount3) + int(amount4) + int(amount6)) > 21:
            query = f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}"
            await self.execute(query=query, commit=True)
            e = discord.Embed(color=0xff5630, title="Blackjack",
                              description=f"{self.bot.user.name} went over 21 and {author.name} won!")
            e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
                        value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}",
                        inline=True)
            e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
                        value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount6}{bot_choice3}",
                        inline=True)
            await msg.edit(embed=e)
            return

        e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
        e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
                    value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}|{card_choice3}", inline=True)
        e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ? | ?", inline=True)

        msg = await ctx.send(embed=e)

        def check(m):
            return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author

        try:
            await self.bot.wait_for('message', check=check, timeout=7.5)
        except:
            if (int(amount1) + int(amount2) + int(amount5)) > (int(amount3) + int(amount4) + int(amount6)):
                winner = author.name
                color = 0xDEADBF
                query = f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}"
                await self.execute(query=query, commit=True)
            else:
                winner = self.bot.user.name
                color = 0xff5630
            await msg.edit(
                embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
            return

        # 3rd screen #

        card_choice4 = cards[random.choice(lst)]

        bot_choice4 = cards[random.choice(lst)]

        amount7 = card_choice3[2]
        amount8 = bot_choice3[2]

        if amount7 is "Q" or amount7 is "K" or amount7 is "J":
            amount7 = 10
        if amount8 is "Q" or amount8 is "K" or amount8 is "J":
            amount8 = 10

        if amount7 is "A":
            amount7 = 11
        if amount8 is "A":
            amount8 = 11

        if (int(amount1) + int(amount2) + int(amount5) + int(amount7)) > 21:
            e = discord.Embed(color=0xff5630, title="Blackjack",
                              description=f"{author.name} went over 21 and {self.bot.user.name} won!")
            e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
                        value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}",
                        inline=True)
            e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
                        value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount5}{bot_choice3}",
                        inline=True)
            await msg.edit(embed=e)
            return
        elif (int(amount3) + int(amount4) + int(amount6) + int(amount8)) > 21:
            query = f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}"
            await self.execute(query=query, commit=True)
            e = discord.Embed(color=0xff5630, title="Blackjack",
                              description=f"{self.bot.user.name} went over 21 and {author.name} won!")
            e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5)}",
                        value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}| {amount7}{card_choice4}",
                        inline=True)
            e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
                        value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount6}{bot_choice3}| {amount8}{bot_choice4}",
                        inline=True)
            await msg.edit(embed=e)
            return

        e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
        e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount7)}",
                    value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}|{card_choice3}| {amount7}{card_choice4}", inline=True)
        e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ? | ? | ?", inline=True)

        msg = await ctx.send(embed=e)
        msg

        def check(m):
            return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author

        try:
            await self.bot.wait_for('message', check=check, timeout=7.5)
        except:
            if (int(amount1) + int(amount2) + int(amount5) + int(amount7)) > (int(amount3) + int(amount4) + int(amount6) + int(amount8)):
                winner = author.name
                color = 0xDEADBF
                query = f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}"
                await self.execute(query=query, commit=True)
            else:
                winner = self.bot.user.name
                color = 0xff5630
            await msg.edit(
                embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
            return

        # 3rd screen #

        card_choice5 = cards[random.choice(lst)]

        bot_choice5 = cards[random.choice(lst)]

        amount9 = card_choice3[2]
        amount10 = bot_choice3[2]

        if amount9 is "Q" or amount9 is "K" or amount9 is "J":
            amount9 = 10
        if amount10 is "Q" or amount10 is "K" or amount10 is "J":
            amount10 = 10

        if amount9 is "A":
            amount9 = 11
        if amount10 is "A":
            amount10 = 11

        if (int(amount1) + int(amount2) + int(amount5) + int(amount9) + int(amount7)) > 21:
            e = discord.Embed(color=0xff5630, title="Blackjack",
                              description=f"{author.name} went over 21 and {self.bot.user.name} won!")
            e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount7)}",
                        value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}| {amount7}{card_choice5}",
                        inline=True)
            e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6) + int(amount8) + int(amount10)}",
                        value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount5}{bot_choice3}| {amount10}{bot_choice3}",
                        inline=True)
            await msg.edit(embed=e)
            return
        elif (int(amount3) + int(amount4) + int(amount6) + int(amount10) + int(amount8)) > 21:
            query = f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}"
            await self.execute(query=query, commit=True)
            e = discord.Embed(color=0xff5630, title="Blackjack",
                              description=f"{self.bot.user.name} went over 21 and {author.name} won!")
            e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount7) + int(amount9)}",
                        value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}{card_choice3}| {amount9}{card_choice5}| {amount7}|{card_choice4}",
                        inline=True)
            e.add_field(name=f"{self.bot.user.name}'s Cards | {int(amount3) + int(amount4) + int(amount6)}",
                        value=f"{amount3}{bot_choice1}| {amount4}{bot_choice2}| {amount6}{bot_choice3}| {amount10}{bot_choice5}| {amount8}{bot_choice4}",
                        inline=True)
            await msg.edit(embed=e)
            return

        e = discord.Embed(color=0xDEADBF, title="Blackjack", description="Type `hit` to hit or wait 7s to end")
        e.add_field(name=f"{author.name}'s Cards | {int(amount1) + int(amount2) + int(amount5) + int(amount9) + int(amount7)}",
                    value=f"{amount1}{card_choice1}| {amount2}{card_choice2}| {amount5}|{card_choice3}| {amount7}{card_choice4}| {amount9}{card_choice5}", inline=True)
        e.add_field(name=f"{self.bot.user.name}'s Cards | ?", value=f"{amount3}{bot_choice1}| ? | ? | ? | ?", inline=True)

        msg = await ctx.send(embed=e)

        def check(m):
            return m.content == 'hit' and m.channel == ctx.message.channel and m.author == author

        try:
            await self.bot.wait_for('message', check=check, timeout=7.5)
        except:
            if (int(amount1) + int(amount2) + int(amount5) + int(amount7) + int(amount9)) > (int(amount3) + int(amount4) + int(amount6) + int(amount8) + int(amount10)):
                winner = author.name
                color = 0xDEADBF
                query = f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}"
                await self.execute(query=query, commit=True)
            else:
                winner = self.bot.user.name
                color = 0xff5630
            await msg.edit(
                embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))
            return

        if (int(amount1) + int(amount2) + int(amount5) + int(amount7) + int(amount9)) > (
                int(amount3) + int(amount4) + int(amount6) + int(amount8) + int(amount10)):
            winner = author.name
            color = 0xDEADBF
            query = f"UPDATE economy SET balance = {int(author_balance + (betting_amount * 1.5))} WHERE userid = {author.id}"
            await self.execute(query=query, commit=True)
        else:
            winner = self.bot.user.name
            color = 0xff5630
        await msg.edit(
            embed=discord.Embed(color=color, title="Blackjack", description=f"Game ended with {winner} winning!"))

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
