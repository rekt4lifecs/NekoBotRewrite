import discord, pymysql, random, time, datetime, asyncio
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import textwrap
import aiohttp, config

class CardGame:
    """Loli Card Gamelol"""

    def __init__(self, bot):
        self.bot = bot

    async def usercheck(self, datab: str, user: discord.Member):
        user = user.id
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        if not db.execute(f'SELECT 1 FROM {datab} WHERE userid = {user}'):
            return False
        else:
            return True

    async def _create_user(self, user_id: int, datab: str = "roleplay"):
        try:
            connection = pymysql.connect(host="localhost",
                                         user="root",
                                         password="rektdiscord",
                                         db="nekobot",
                                         port=3306)
            db = connection.cursor()
            # userid, cardid1, cardid2, cardid3, cardid4, cardid5, cardid6 lastdaily, key
            db.execute(f"INSERT INTO {datab} VALUES ({user_id}, 0, 0, 0, 0, 0, 0, 0)")
            connection.commit()
        except:
            pass

    @commands.group()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def card(self, ctx: commands.Context):
        """Loli Card Game OwO"""
        try:
            if await self.usercheck('roleplay', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        if ctx.invoked_subcommand is None:
            return await ctx.send("A loli roleplaying card game ofc!\n\n**Commands**\n"
                                  "**n!card daily** - Get your daily cards\n"
                                  "**n!card display** - Display a card of yours\n"
                                  "**n!card list** - Lists your cards\n"
                                  "**n!card sell** - Sell a card\n"
                                  "**n!card fight** - Fight a user OwO\n"
                                  "**n!card transfer** - Transfer a card")

    @card.command(name='transfer')
    async def card_transfer(self, ctx, card_num: int, user: discord.Member):
        """Transfer a card to a user"""
        await ctx.send("**Coming Soon.**", delete_after=5)
        # connection = pymysql.connect(host="localhost",
        #                              user="root",
        #                              password="rektdiscord",
        #                              db="nekobot",
        #                              port=3306)
        # db = connection.cursor()
        # if not db.execute(f"SELECT 1 FROM roleplay WHERE userid = {ctx.message.author.id}"):
        #     return await ctx.send(f"{ctx.message.author.mention}, you don't have any cards!")
        # elif user.bot:
        #     return await ctx.send("**You can't transfer cards to bots**")
        # elif not db.execute(f"SELECT 1 FROM roleplay WHERE userid = {user.id}"):
        #     return await ctx.send(f"{user.name} doesn't have any cards.")
        # db.execute(f"SELECT cardid{card_num} FROM roleplay WHERE userid = {ctx.message.author.id}")
        # cardid = int(db.fetchone()[0])
        # if cardid == 0:
        #     return await ctx.send("**Empty Slot**")
        # else:
        #     db.execute(f"SELECT character_name FROM roleplay_cards WHERE cardid = {cardid}")
        #     card_name = db.fetchone()[0]
        #
        # db.execute(
        #     f"SELECT cardid1, cardid2, cardid3, cardid4, cardid5, cardid6 FROM roleplay WHERE userid = {user.id}")
        # allcards = db.fetchall()
        # cardid1 = int(allcards[0][0])
        # cardid2 = int(allcards[0][1])
        # cardid3 = int(allcards[0][2])
        # cardid4 = int(allcards[0][3])
        # cardid5 = int(allcards[0][4])
        # cardid6 = int(allcards[0][5])
        # if cardid1 == 0:
        #     cardid = "cardid1"
        # elif cardid2 == 0:
        #     cardid = "cardid2"
        # elif cardid3 == 0:
        #     cardid = "cardid3"
        # elif cardid4 == 0:
        #     cardid = "cardid4"
        # elif cardid5 == 0:
        #     cardid = "cardid5"
        # elif cardid6 == 0:
        #     cardid = "cardid6"
        # else:
        #     return await ctx.send(f"**{user.name} is out of slots!**")
        #
        # await ctx.send(f"Are you sure you want to give {user.name}, {card_name}")
        #
        # def check(m):
        #     return m.author == ctx.message.author and m.channel == ctx.message.channel
        #
        # try:
        #     msg = await self.bot.wait_for('message', check=check, timeout=15.0)
        # except asyncio.TimeoutError:
        #     return await ctx.send("**Timed out...**")
        # if str(msg.content).lower().startswith("yes"):
        #     db.execute(f"SELECT cardid{card_num} FROM roleplay WHERE userid = {user.id}")
        #     cardidxx = int(db.fetchone()[0])
        #     db.execute(f"UPDATE roleplay SET {cardid} = 0 WHERE userid = {ctx.message.author.id}")
        #     connection.commit()
        #     db.execute(f"UPDATE roleplay SET {cardid} = {cardidxx} WHERE userid = {user.id}")
        #     connection.commit()
        #     await ctx.send(f"**Successfully transferred {card_name} from {ctx.message.author.name} to {user.name}!**")
        # else:
        #     return await ctx.send("Transaction cancelled.")

    @card.command(name='fight', aliases=['battle'])
    async def card_battle(self, ctx, user: discord.Member):
        """Fight a user OwO"""
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        author = ctx.message.author
        if not db.execute(f"SELECT 1 FROM roleplay WHERE userid = {author.id}"):
            return await ctx.send(f"{author.mention}, you don't have any cards!")
        elif not db.execute(f"SELECT 1 FROM roleplay WHERE userid = {user.id}"):
            return await ctx.send(f"{user.name} doesn't have any cards.")
        await ctx.send(f"{user.mention}, would you like to battle {author.mention}? Will timout in 15 seconds.")

        def check_user(m):
            return m.author == user and m.channel == ctx.message.channel

        def check_author(m):
            return m.author == author and m.channel == ctx.message.channel

        try:
            msg = await self.bot.wait_for('message', check=check_user, timeout=15.0)
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="Battle cancelled."))
            return

        if msg.content == "Yes" or msg.content == "yes":
            await ctx.send(f"{author.mention}, please select a card.")
            try:
                msg = await self.bot.wait_for('message', check=check_author, timeout=15.0)
            except asyncio.TimeoutError:
                return await ctx.send(embed=discord.Embed(color=0xff5630, description="Battle cancelled."))
            try:
                msgcontent = int(msg.content)
            except:
                return await ctx.send("Invalid card. Returning...")
            if msgcontent <= 0:
                return await ctx.send("Invalid card. Returning...")
            elif msgcontent > 6:
                return await ctx.send("Invalid card. Returning...")
            db.execute(f"SELECT cardid{msgcontent} FROM roleplay WHERE userid = {author.id}")
            author_card = int(db.fetchone()[0])
            if author_card == 0:
                return await ctx.send(f"{author.mention}, you don't have a card in that slot.")
            else:
                await ctx.send(f"{user.mention}, please select a card.")
                try:
                    msg = await self.bot.wait_for('message', check=check_user, timeout=15.0)
                except asyncio.TimeoutError:
                    return await ctx.send(embed=discord.Embed(color=0xff5630, description="Battle cancelled."))
                try:
                    msgcontent = int(msg.content)
                except:
                    return await ctx.send("Invalid card. Returning...")
                if msgcontent <= 0:
                    return await ctx.send("Invalid card. Returning...")
                elif msgcontent > 6:
                    return await ctx.send("Invalid card. Returning...")
                db.execute(f"SELECT cardid{msgcontent} FROM roleplay WHERE userid = {user.id}")
                user_card = int(db.fetchone()[0])
                if user_card == 0:
                    return await ctx.send(f"{user.mention}, you don't have a card in that slot.")
                else:
                    db.execute(
                        f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {author_card}")
                    all_author_cards = db.fetchall()
                    author_card_name = all_author_cards[0][0]
                    author_card_attack = all_author_cards[0][1]
                    author_card_defense = all_author_cards[0][2]
                    db.execute(f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {user_card}")
                    all_user_cards = db.fetchall()
                    user_card_name = all_user_cards[0][0]
                    user_card_attack = all_user_cards[0][1]
                    user_card_defense = all_user_cards[0][2]
                    msg = await ctx.send(
                        embed=discord.Embed(color=0xDEADBF, title=f"{author_card_name} ({author.name}) |\n"
                                                                  f" {user_card_name} ({user.name})",
                                            description=f"**{author.name}** vs **{user.name}**"))
                    await asyncio.sleep(random.randint(3, 6))
                    if (int(author_card_attack) + int(author_card_defense)) > (
                            int(user_card_attack) + int(user_card_defense)):
                        await msg.edit(
                            embed=discord.Embed(color=0xDEADBF, title=f"{author_card_name} ({author.name}) |\n"
                                                                      f" {user_card_name} ({user.name})",
                                                description=f"**{author.name}** vs **{user.name}**\n"
                                                            f"**{author.name}** Beat **{user.name}**"))
                    elif (int(author_card_attack) + int(author_card_defense)) < (
                            int(user_card_attack) + int(user_card_defense)):
                        await msg.edit(
                            embed=discord.Embed(color=0xDEADBF, title=f"{author_card_name} ({author.name}) |\n"
                                                                      f" {user_card_name} ({user.name})",
                                                description=f"**{author.name}** vs **{user.name}**\n"
                                                            f"**{user.name}** Beat **{author.name}**"))
        else:
            return await ctx.send("Battle cancelled.")

    @card.command(name='check')
    @commands.is_owner()
    async def check_check_lol(self, ctx):
        """Check test"""
        author = ctx.message.author
        await ctx.send("Check Start.")

        def check(m):
            return m.author == author and m.channel == ctx.message.channel

        msg = await self.bot.wait_for('message', check=check)
        await ctx.send(f"{msg.attachments[0]}")

    @card.command(name='daily')
    async def card_daily(self, ctx):
        """Get your card daily"""
        async with aiohttp.ClientSession(headers={"Authorization": config.dbots_key}) as cs:
            async with cs.get(f'https://discordbots.org/api/bots/310039170792030211/check?userId={ctx.message.author.id}') as r:
                res = await r.json()
        if not res['voted'] == 1:
            return await ctx.send("You haven't voted today ;c")
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        i = db.execute(f"SELECT 1 FROM roleplay WHERE userid = {ctx.message.author.id}")
        if i == 0:
            db.execute(f"INSERT INTO roleplay VALUES ({ctx.message.author.id}, 0, 0, 0, 0, 0, 0, 0)")
            connection.commit()
        author = ctx.message.author
        db.execute(f"SELECT lastdaily FROM roleplay WHERE userid = {author.id}")
        lastdaily = int(db.fetchone()[0])
        lastdaily = datetime.datetime.utcfromtimestamp(int(lastdaily)).strftime("%d")
        today = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
        if today == lastdaily:
            tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1),
                                                 hour=0, minute=0, second=0)
            delta = tomorrow - datetime.datetime.now()
            timeleft = time.strftime("%H", time.gmtime(delta.seconds))
            timeleft_m = time.strftime("%M", time.gmtime(delta.seconds))
            await ctx.send(f"Wait another {timeleft}h {timeleft_m}m before using daily again...")
            return
        db.execute(
            f"SELECT cardid1, cardid2, cardid3, cardid4, cardid5, cardid6 FROM roleplay WHERE userid = {author.id}")
        allcards = db.fetchall()
        cardid1 = int(allcards[0][0])
        cardid2 = int(allcards[0][1])
        cardid3 = int(allcards[0][2])
        cardid4 = int(allcards[0][3])
        cardid5 = int(allcards[0][4])
        cardid6 = int(allcards[0][5])
        if cardid1 == 0:
            dailycard = "cardid1"
        elif cardid2 == 0:
            dailycard = "cardid2"
        elif cardid3 == 0:
            dailycard = "cardid3"
        elif cardid4 == 0:
            dailycard = "cardid4"
        elif cardid5 == 0:
            dailycard = "cardid5"
        elif cardid6 == 0:
            dailycard = "cardid6"
        else:
            return await ctx.send("**All your card slots are full.**")
        list_ = [
            "Shiro",
            "Kafuu Chino",
            "Toujou Koneko",
            "Aihara Enju",
            "Yoshino",
            "Takanashi Rikka",
            "Tsutsukakushi Tsukiko",
            "Aisaka Taiga",
            "Oshino Shinobu",
            "Hasegawa Kobato",
            "Hibiki",
            "Terminus Est",
            "Tachibana Kanade",
            "Noel",
            "Itsuka Kotori",
            "Illyasviel Von Einzbern",
            "Sprout Tina",
            "Yazawa Nico",
            "Izumi Konata",
            "Konjiki No Yami",
            "Shana",
            "Gokou Ruri",
            "Sigtuna Yurie",
            "Shimakaze",
            "Yuuki Mikan",
            "Victorique De Blois",
            "Kanzaki Aria",
            "Cirno",
            "Wendy Marvell",
            "Nakano Azusa",
            "Akatsuki",
            "Yaya",
            "Yukihira Furano",
            "Uni",
            "Akatsuki",
            "Nyaruko",
            "Azuki Azusa",
            "Hachikuji Mayoi",
            "Amatsukaze",
            "Flandre Scarlet",
            "Hiiragi Kagami",
            "Tatsumaki",
            "Louise Fran\u00e7oise Le Blanc De La Valli\u00e8re",
            "Kaname Madoka",
            "Sakura Kyouko",
            "Hoshimiya Kate",
            "Fear Kubrick",
            "Sengoku Nadeko",
            "Kirima Sharo",
            "Noumi Kudryavka",
            "Kanna",
            "chifuyu_himeki"
        ]
        character_loli = str(random.choice(list_)).lower().replace(' ', '_')
        character_code = random.randint(0, 1000000000)
        db.execute(f"UPDATE roleplay SET lastdaily = {int(time.time())} WHERE userid = {author.id}")
        connection.commit()
        db.execute(f"UPDATE roleplay SET {dailycard} = {character_code} WHERE userid = {author.id}")
        connection.commit()
        db.execute(f"INSERT INTO roleplay_cards VALUES ({character_code},"
                   f"\"{character_loli}\","
                   f"{random.randint(1, 50)},"
                   f"{random.randint(1, 50)})")
        connection.commit()
        await ctx.send(f"Given character **{character_loli.replace('_', ' ').title()}!**")

    def _generate_card(self, character: str, num: int, attack: int, defense: int):
        card_name = f"data/{character}.jpg"
        img = Image.open('data/card.jpg')
        _character = Image.open(card_name).resize((314, 313))

        draw = ImageDraw.Draw(img)
        title_font = ImageFont.truetype("data/fonts/card.ttf", 40)
        lower_font = ImageFont.truetype("data/fonts/card.ttf", 20)
        desc_font = ImageFont.truetype("data/fonts/card.ttf", 16)

        img.paste(_character, (52, 114))

        if character == 'kanna':
            description = "Be sure to keep this loli charged. Very thicc thighs."
        elif character == 'yaya':
            description = "She'll be your puppet if you promise to marry her."
        elif character == 'yoshino':
            description = "She must be a happy loli. Word of the wise never have her lose Yoshinon."
        elif character == 'toujou_koneko':
            description = "A Neko Loli who will not kindly treat perverted actions."
        elif character == 'terminus_est':
            description = "A sword who can transform into a loli. For some reason is just fine wearing only knee socks but not being fully naked."
        elif character == 'azuki_azusa':
            description = "A hard working loli who pretends to be rich. Likes animals and works a lot of jobs to afford the act."
        elif character == 'itsuka_kotori':
            description = "A bipolar loli. The color of the ribbon determines her personally as weak for white and strong for black."
        elif character == 'tachibana_kanade':
            description = "An \"Angel\" who develops her own body to defend."
        elif character == 'nyaruko':
            description = "An obessive otaku loli who will kill anyone that dares attempt to harm what she loves. "
        elif character == 'cirno':
            description = "A ice fairy who never backs down from a challenge. She is very weak in respect to others but won't stop trying."
        elif character == 'flandre_scarlet':
            description = "She respects her sister so much that she never leaves the mansion due to her orders. Is nice, quiet, and a tad nuts. "
        elif character == 'shiro':
            description = "Genius gamer who is excellent at both strategy and in first person shooters. She will quickly master languages."
        elif character == 'aihara_enju':
            description = "A rabbit type girl who will protect her friends. Can get jealous even to friends and tries to marry her partner at every chance."
        elif character == 'takanashi_rikka':
            description = "A loli suffering from \"8th grade syndrome\" who believes she has the power of the tyrants's eye an will always walk around with an umbrella."
        elif character == 'tsutsukakushi_tsukiko':
            description = "A gluttonous loli who will eat numerous snacks and cannot show emotion. Thinks of herself as childish."
        elif character == 'aisaka_taiga':
            description = "Kind to those she trusts while aggressive to others. She hates he height pointed out or being called the palm top tiger."
        elif character == 'hasegawa_kobato':
            description = "A very shy loli who enjoys cosplaying. She is almost always dressed up in a cosplay of her favorite gothic vampire."
        elif character == 'sprout_tina':
            description = "A noctural loli. She will be sleepy during the day; however, when night falls she becomes an excellent sniper Who follows every order."
        elif character == 'konjiki_no_yami':
            description = "Attacks those that talk about something she doesn't like and hates perverted people."
        elif character == 'yukihira_furano':
            description = "A quiet girl that will insert sexual or vulgar words or phrases into sentences. Is also a part of the \"Reject Five\""
        elif character == 'tatsumaki':
            description = "Arrogant and overconfident. She considers her job as a duty and also can get bored while not fighting monsters."
        elif character == 'victorique_de_blois':
            description = "Bored by a normal life so she wants cases or other things to entertain her. She dislikes most strangers. She is also very intelligent."
        else:
            description = ""

        draw.text((37, 23), character.replace('_', ' '), (0, 0, 0), title_font)
        draw.text((255, 550), str(attack), (0, 0, 0), lower_font)
        draw.text((344, 550), str(defense), (0, 0, 0), lower_font)
        draw.text((40, 477), textwrap.fill(description, 37), (0, 0, 0), font=desc_font)

        img.save(f"data/cards/{num}.png")

    @card.command(name='sell')
    async def card_sell(self, ctx, num: int):
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        try:
            if await self.usercheck('roleplay', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        if num > 6 or num < 1:
            return await ctx.send("**Out of card range.**")
        if num == 1:
            cardnum = "cardid1"
        elif num == 2:
            cardnum = "cardid2"
        elif num == 3:
            cardnum = "cardid3"
        elif num == 4:
            cardnum = "cardid4"
        elif num == 5:
            cardnum = "cardid5"
        elif num == 6:
            cardnum = "cardid6"
        author = ctx.message.author
        db.execute(f"SELECT {cardnum} FROM roleplay WHERE userid = {author.id}")
        selectd = db.fetchone()[0]
        if int(selectd) == 0:
            return await ctx.send("**No cards in that slot...**")

        db.execute(f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {int(selectd)}")
        allcards = db.fetchall()

        cardname = str(allcards[0][0])
        cardname_en = str(allcards[0][0]).replace('_', ' ').title()
        attack = int(allcards[0][1])
        defense = int(allcards[0][2])

        cardprice = int(random.randint(10000, 15000) + (((attack * .25) + (defense * .25)) * 1000))

        await ctx.send(f"{author.mention}, type `yes` to sell **{cardname_en}** for {cardprice}")

        def check(m):
            return m.content == 'yes' and m.channel == ctx.message.channel and m.author == author

        try:
            await self.bot.wait_for('message', check=check, timeout=15.0)
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="Cancelled Transaction."))
            return

        await ctx.send(f"Sold {cardname} for {cardprice}")

        hasaccount = db.execute(f"SELECT 1 FROM economy WHERE userid = {author.id}")
        if hasaccount == 0:
            db.execute(f"INSERT INTO economy VALUES ({author.id}, 0, 0)")
            connection.commit()

        db.execute(f"SELECT balance FROM economy WHERE userid = {author.id}")
        balance = int(db.fetchone()[0])
        db.execute(f"UPDATE economy SET balance = {int(balance + cardprice)} WHERE userid = {author.id}")
        connection.commit()
        db.execute(f"UPDATE roleplay SET {cardnum} = 0 WHERE userid = {author.id}")
        connection.commit()

    @card.command(name='list')
    async def card_list(self, ctx):
        """List your cards"""
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        try:
            if await self.usercheck('roleplay', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        author = ctx.message.author
        db.execute(
            f"SELECT cardid1, cardid2, cardid3, cardid4, cardid5, cardid6 FROM roleplay WHERE userid = {author.id}")
        allcards = db.fetchall()[0]

        card1 = db.execute(
            f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {int(allcards[0])}")
        if card1 != 0:
            all_ = db.fetchall()[0]
            card1 = str(all_[0]).replace("_", " ").title()
            card1_a = all_[1]
            card1_d = all_[2]
        else:
            card1 = "Empty"
            card1_a = 0
            card1_d = 0

        card2 = db.execute(
            f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {int(allcards[1])}")
        if card2 != 0:
            all_ = db.fetchall()[0]
            card2 = str(all_[0]).replace("_", " ").title()
            card2_a = all_[1]
            card2_d = all_[2]
        else:
            card2 = "Empty"
            card2_a = 0
            card2_d = 0

        card3 = db.execute(
            f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {int(allcards[2])}")
        if card3 != 0:
            all_ = db.fetchall()[0]
            card3 = str(all_[0]).replace("_", " ").title()
            card3_a = all_[1]
            card3_d = all_[2]
        else:
            card3 = "Empty"
            card3_a = 0
            card3_d = 0

        card4 = db.execute(
            f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {int(allcards[3])}")
        if card4 != 0:
            all_ = db.fetchall()[0]
            card4 = str(all_[0]).replace("_", " ").title()
            card4_a = all_[1]
            card4_d = all_[2]
        else:
            card4 = "Empty"
            card4_a = 0
            card4_d = 0

        card5 = db.execute(
            f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {int(allcards[4])}")
        if card5 != 0:
            all_ = db.fetchall()[0]
            card5 = str(all_[0]).replace("_", " ").title()
            card5_a = all_[1]
            card5_d = all_[2]
        else:
            card5 = "Empty"
            card5_a = 0
            card5_d = 0

        card6 = db.execute(
            f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {int(allcards[5])}")
        if card6 != 0:
            all_ = db.fetchall()[0]
            card6 = str(all_[0]).replace("_", " ").title()
            card6_a = all_[1]
            card6_d = all_[2]
        else:
            card6 = "Empty"
            card6_a = 0
            card6_d = 0

        embed = discord.Embed(color=0xDEADBF,
                              title=f"{author.name}'s Cards",
                              description=f"1. **{card1}** - Attack: **{card1_a}** - Defense: **{card1_d}**\n"
                                          f"2. **{card2}** - Attack: **{card2_a}** - Defense: **{card2_d}**\n"
                                          f"3. **{card3}** - Attack: **{card3_a}** - Defense: **{card3_d}**\n"
                                          f"4. **{card4}** - Attack: **{card4_a}** - Defense: **{card4_d}**\n"
                                          f"5. **{card5}** - Attack: **{card5_a}** - Defense: **{card5_d}**\n"
                                          f"6.** {card6}** - Attack: **{card6_a}** - Defense: **{card6_d}**")
        await ctx.send(embed=embed)

    @card.command(name='display')
    async def card_display(self, ctx, num: int):
        """Display your card(s)"""
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        try:
            if await self.usercheck('roleplay', ctx.message.author) is False:
                await self._create_user(ctx.message.author.id)
        except:
            pass
        if num > 6 or num < 1:
            return await ctx.send("**Out of card range.**")
        if num == 1:
            cardnum = "cardid1"
        elif num == 2:
            cardnum = "cardid2"
        elif num == 3:
            cardnum = "cardid3"
        elif num == 4:
            cardnum = "cardid4"
        elif num == 5:
            cardnum = "cardid5"
        elif num == 6:
            cardnum = "cardid6"
        author = ctx.message.author
        db.execute(f"SELECT {cardnum} FROM roleplay WHERE userid = {author.id}")
        if int(db.fetchone()[0]) == 0:
            return await ctx.send("**Empty Slot**")
        num = random.randint(1, 1000000000)
        db.execute(f"SELECT {cardnum} FROM roleplay WHERE userid = {author.id}")
        cardid = int(db.fetchone()[0])
        db.execute(f"SELECT character_name, attack, defense FROM roleplay_cards WHERE cardid = {cardid}")
        allitems = db.fetchall()
        character_name = str(allitems[0][0])
        character_name_en = str(allitems[0][0]).replace('_', ' ').title()
        attack = int(allitems[0][1])
        defense = int(allitems[0][2])
        self._generate_card(character_name, num, attack, defense)

        embed = discord.Embed(color=0xDEADBF, title=character_name_en)
        embed.add_field(name="Attack", value=str(attack))
        embed.add_field(name="Defense", value=str(defense))

        await ctx.send(file=discord.File(f'data/cards/{num}.png'), embed=embed.set_image(url=f'attachment://{num}.png'))

    @card.command(name='generate')
    @commands.is_owner()
    async def card_gen(self, ctx, character: str = "shiro", attack: int = 1, defense: int = 1):
        """Recieve your dailies"""
        card_name = f"data/{character}.jpg"
        img = Image.open('data/card.jpg')
        _character = Image.open(card_name).resize((314, 313))

        draw = ImageDraw.Draw(img)
        title_font = ImageFont.truetype("data/fonts/card.ttf", 40)
        lower_font = ImageFont.truetype("data/fonts/card.ttf", 20)

        img.paste(_character, (52, 114))

        draw.text((37, 23), character.replace('_', ' '), (0, 0, 0), title_font)
        draw.text((255, 550), str(attack), (0, 0, 0), lower_font)
        draw.text((344, 550), str(defense), (0, 0, 0), lower_font)

        num = random.randint(1, 10000000)
        img.save(f"data/cards/{num}.png")
        await ctx.send(file=discord.File(f"data/cards/{num}.png"),
                       embed=discord.Embed(color=0xDEADBF).set_image(url=f'attachment://{num}.png'))


def setup(bot):
    bot.add_cog(CardGame(bot))