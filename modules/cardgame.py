import discord, random, time, datetime, asyncio
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import textwrap
import aiohttp, config, ujson
import rethinkdb as r
import os
from prettytable import PrettyTable

# Languages
languages = ["english", "weeb", "tsundere", "polish", "spanish", "french"]
lang = {}

for l in languages:
    with open("lang/%s.json" % l, encoding="utf-8") as f:
        lang[l] = ujson.load(f)

def getlang(la:str):
    return lang.get(la, None)

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
    "Kaname Madoka",
    "Sakura Kyouko",
    "Hoshimiya Kate",
    "Fear Kubrick",
    "Sengoku Nadeko",
    "Kirima Sharo",
    "Noumi Kudryavka",
    "Kanna",
    "chifuyu_himeki",
    "holo",
    "dva"
] #"Louise Francoise Le Blanc De La Valliere",

class CardGame:
    """Loli Card Gamelol"""

    def __init__(self, bot):
        self.bot = bot

    async def __has_account(self, user:int):
        if await r.table("cardgame").get(str(user)).run(self.bot.r_conn):
            return True
        else:
            return False

    async def __create_account(self, user:int):
        data = {
            "id": str(user),
            "lastdaily": "0",
            "cards": []
        }
        await r.table("cardgame").insert(data).run(self.bot.r_conn)

    async def __check_for_user(self, user:int):
        if not await self.__has_account(user):
            await self.__create_account(user)

    @commands.group()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def card(self, ctx: commands.Context):
        """Loli Card Game OwO"""
        lang = await self.bot.redis.get(f"{ctx.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        await self.__check_for_user(ctx.author.id)

        if ctx.invoked_subcommand is None:
            return await ctx.send(getlang(lang)["cardgame"]["card_help"])

    @card.command(name="transfer")
    async def card_transfer(self, ctx, card_number, user:discord.Member):
        """Transfer cards to other users"""

        if user == ctx.author:
            return await ctx.send("You can't send yourself cards")
        elif user.bot:
            return await ctx.send("You can't send bots cards.")

        try:
            card_number = int(card_number)
        except:
            return await ctx.send("Not a valid number")

        if card_number > 6 or card_number <= 0:
            return await ctx.send("Not a valid card number.")

        await self.__check_for_user(ctx.author.id)
        await self.__check_for_user(user.id)

        author_data = await r.table("cardgame").get(str(ctx.author.id)).run(self.bot.r_conn)
        author_cards = author_data["cards"]
        user_data = await r.table("cardgame").get(str(user.id)).run(self.bot.r_conn)
        user_cards = user_data["cards"]

        if len(user_cards) >= 6:
            return await ctx.send("%s has no slots left" % user.mention)

        try:
            card = author_cards[card_number-1]
        except:
            return await ctx.send("Not a valid card.")

        user_cards.append(card)

        newdata = {
            "cards": user_cards
        }

        await r.table("cardgame").get(str(ctx.author.id)).update({"cards": r.row["cards"].delete_at(card_number-1)}).run(self.bot.r_conn)
        await r.table("cardgame").get(str(user.id)).update(newdata).run(self.bot.r_conn)
        await ctx.send("Transferred card to %s!"% user.mention)

    # @card.command(name='fight', aliases=['battle'])
    # async def card_battle(self, ctx, user: discord.Member):
    #     """Fight a user OwO"""
    #     lang = await self.bot.redis.get(f"{ctx.author.id}-lang")
    #     if lang:
    #         lang = lang.decode('utf8')
    #     else:
    #         lang = "english"
    #     author = ctx.author
    #
    #     await self.__check_for_user(ctx.author.id)
    #
    #     author_data = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
    #     if len(author_data["cards"]) == 0:
    #         return await ctx.send("%s you don't have any cards." % author.mention)
    #     user_data = await r.table("cardgame").get(str(user.id)).run(self.bot.r_conn)
    #     if len(user_data["cards"]) == 0:
    #         return await ctx.send("%s has no cards." % user.mention)
    #
    #     await ctx.send(getlang(lang)["cardgame"]["battle"]["confirm"].format(user, author))
    #
    #     def check_user(m):
    #         return m.author == user and m.channel == ctx.message.channel
    #
    #     def check_author(m):
    #         return m.author == author and m.channel == ctx.message.channel
    #
    #     try:
    #         msg = await self.bot.wait_for('message', check=check_user, timeout=15.0)
    #     except asyncio.TimeoutError:
    #         await ctx.send(embed=discord.Embed(color=0xff5630,
    #                                            description=getlang(lang)["cardgame"]["battle"]["cancelled"]))
    #         return
    #
    #     if msg.content.lower() == "yes":
    #         await ctx.send(getlang(lang)["cardgame"]["battle"]["author_select"].format(author))
    #         try:
    #             msg = await self.bot.wait_for('message', check=check_author, timeout=15.0)
    #         except asyncio.TimeoutError:
    #             return await ctx.send(embed=discord.Embed(color=0xff5630,
    #                                                       description=getlang(lang)["cardgame"]["battle"]["cancelled"]))
    #         try:
    #             msgcontent = int(msg.content)
    #         except:
    #             return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid"])
    #         if msgcontent <= 0:
    #             return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid"])
    #         elif msgcontent > 6:
    #             return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid"])
    #
    #         try:
    #             author_card = author_data["cards"][msgcontent]
    #         except:
    #             return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid_slot"].format(author))
    #
    #         else:
    #             await ctx.send(getlang(lang)["cardgame"]["battle"]["author_select"].format(user))
    #             try:
    #                 msg = await self.bot.wait_for('message', check=check_user, timeout=15.0)
    #             except asyncio.TimeoutError:
    #                 return await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["cardgame"]["battle"]["cancelled"]))
    #             try:
    #                 msgcontent = int(msg.content)
    #             except:
    #                 return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid"])
    #             if msgcontent <= 0:
    #                 return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid"])
    #             elif msgcontent > 6:
    #                 return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid"])
    #
    #             try:
    #                 user_card = user_data["cards"][msgcontent]
    #             except:
    #                 return await ctx.send(getlang(lang)["cardgame"]["battle"]["invalid_slot"].format(author))
    #
    #             author_card_name = author_card["name"]
    #             author_card_attack = author_card["attack"]
    #             author_card_defense = author_card["defense"]
    #
    #             user_card_name = user_card["name"]
    #             user_card_attack = user_card["attack"]
    #             user_card_defense = user_card["defense"]
    #             msg = await ctx.send(
    #                 embed=discord.Embed(color=0xDEADBF, title=f"{author_card_name} ({author.name}) |\n"
    #                                                           f" {user_card_name} ({user.name})",
    #                                     description=f"**{author.name}** vs **{user.name}**"))
    #             await asyncio.sleep(random.randint(3, 6))
    #             if (int(author_card_attack) + int(author_card_defense)) > (
    #                     int(user_card_attack) + int(user_card_defense)):
    #                 await msg.edit(
    #                     embed=discord.Embed(color=0xDEADBF, title=f"{author_card_name} ({author.name}) |\n"
    #                                                               f" {user_card_name} ({user.name})",
    #                                         description=f"**{author.name}** vs **{user.name}**\n"
    #                                                     f"**{author.name}** Beat **{user.name}**"))
    #             elif (int(author_card_attack) + int(author_card_defense)) < (
    #                     int(user_card_attack) + int(user_card_defense)):
    #                 await msg.edit(
    #                     embed=discord.Embed(color=0xDEADBF, title=f"{author_card_name} ({author.name}) |\n"
    #                                                               f" {user_card_name} ({user.name})",
    #                                         description=f"**{author.name}** vs **{user.name}**\n"
    #                                                     f"**{user.name}** Beat **{author.name}**"))
    #     else:
    #         return await ctx.send(getlang(lang)["cardgame"]["battle"]["cancelled"])

    @card.command(name='daily')
    async def card_daily(self, ctx):
        """Get your card daily"""
        lang = await self.bot.redis.get(f"{ctx.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        await self.__check_for_user(ctx.author.id)

        data = await r.table("cardgame").get(str(ctx.author.id)).run(self.bot.r_conn)
        lastdaily = int(data["lastdaily"])
        cards = data["cards"]

        lastdaily = datetime.datetime.utcfromtimestamp(lastdaily).strftime("%d")
        today = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")

        author = ctx.message.author

        if today == lastdaily:
            tommorow = datetime.datetime.now() + datetime.timedelta(1)
            midnight = datetime.datetime(year=tommorow.year, month=tommorow.month,
                                         day=tommorow.day, hour=0, minute=0, second=0)
            m, s = divmod((midnight - datetime.datetime.now()).seconds, 60)
            h, m = divmod(m, 60)
            return await ctx.send("You have %s hours and %s minutes until your next daily." % (h, m,))

        if len(cards) >= 6:
            return await ctx.send(getlang(lang)["cardgame"]["daily"]["slots_full"])

        character_loli = str(random.choice(list_)).lower().replace(' ', '_')

        cards.append({
            "name": character_loli,
            "attack": random.randint(1, 50),
            "defense": random.randint(1, 50)
        })

        newdata = {
            "lastdaily": str(int(time.time())),
            "cards": cards
        }

        await r.table("cardgame").get(str(author.id)).update(newdata).run(self.bot.r_conn)
        await ctx.send(getlang(lang)["cardgame"]["daily"]["given_char"].format(character_loli.replace('_', ' ').title()))

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
        elif character == "holo":
            description = ""
        elif character == "dva":
            description = ""
        else:
            description = ""

        draw.text((37, 23), character.replace('_', ' '), (0, 0, 0), title_font)
        draw.text((255, 550), str(attack), (0, 0, 0), lower_font)
        draw.text((344, 550), str(defense), (0, 0, 0), lower_font)
        draw.text((40, 477), textwrap.fill(description, 37), (0, 0, 0), font=desc_font)

        img.save(f"data/cards/{num}.png")

    @card.command(name='sell')
    async def card_sell(self, ctx, num: int):
        """Sell a card"""
        await self.__check_for_user(ctx.author.id)
        if num > 6 or num < 1:
            return await ctx.send("**Out of card range.**")

        author = ctx.message.author
        data = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        if not await r.table("economy").get(str(author.id)).run(self.bot.r_conn):
            return await ctx.send("❌ | **You don't have a bank account to sell your cards, make one with `n!register`**")

        try:
            card = cards[num-1]
        except:
            return await ctx.send("No cards in this slot...")

        cardname = card["name"]
        cardname_en = str(card["name"]).replace('_', ' ').title()
        attack = card["attack"]
        defense = card["defense"]

        cardprice = int(random.randint(10000, 15000) + (((attack * .25) + (defense * .25)) * 1000))

        await ctx.send(f"{author.mention}, type `yes` to sell **{cardname_en}** for {cardprice}")

        def check(m):
            return m.channel == ctx.message.channel and m.author == author

        try:
            x = await self.bot.wait_for('message', check=check, timeout=15.0)
            if not str(x.content).lower() == "yes":
                return await ctx.send("❌ | **Cancelled Transaction.**")
        except asyncio.TimeoutError:
            await ctx.send("❌ | **Cancelled Transaction.**")
            return

        await r.table("cardgame").get(str(author.id)).update({"cards": r.row["cards"].delete_at(num-1)}).run(self.bot.r_conn)
        economy = await r.table("economy").get(str(author.id)).run(self.bot.r_conn)
        await r.table("economy").get(str(author.id)).update({"balance": economy["balance"] + cardprice}).run(self.bot.r_conn)

        await ctx.send(f"Sold {cardname} for {cardprice}")

    @card.command(name='list')
    async def card_list(self, ctx):
        """List your cards"""
        await self.__check_for_user(ctx.author.id)
        author = ctx.message.author

        data = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        table = PrettyTable()
        table.field_names = ["Number", "Card", "Attack", "Defense"]

        cardnum = 0
        displaynum = 1
        for x in range(6):
            try:
                card = cards[cardnum]
                table.add_row([displaynum, card["name"], card["attack"], card["defense"]])
            except:
                table.add_row([displaynum, "Empty", "0", "0"])

            cardnum += 1
            displaynum += 1

        await ctx.send("```\n%s\n```" % table)

    @card.command(name='display')
    async def card_display(self, ctx, num: int):
        """Display your card(s)"""
        await ctx.trigger_typing()
        await self.__check_for_user(ctx.author.id)
        if num > 6 or num < 1:
            return await ctx.send("**Out of card range.**")

        data = await r.table("cardgame").get(str(ctx.author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        author = ctx.message.author

        try:
            card = cards[num-1]
        except:
            return await ctx.send("Empty Slot...")

        num = ctx.author.id

        character_name = card["name"]
        character_name_en = str(character_name).replace('_', ' ').title()
        attack = card["attack"]
        defense = card["defense"]
        self._generate_card(character_name, num, attack, defense)

        embed = discord.Embed(color=0xDEADBF, title=character_name_en)
        embed.add_field(name="Attack", value=str(attack))
        embed.add_field(name="Defense", value=str(defense))

        await ctx.send(file=discord.File(f'data/cards/{num}.png'), embed=embed.set_image(url=f'attachment://{num}.png'))
        os.remove("data/cards/%s.png" % num)

    @card.command(name='generate', hidden=True)
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


    @card.command(name='forcegive', hidden=True)
    @commands.is_owner()
    async def forcegive(self, ctx, user:discord.Member=None):
        if user is None:
            user = ctx.author
        character_loli = str(random.choice(list_)).lower().replace(' ', '_')
        data = await r.table("cardgame").get(str(user.id)).run(self.bot.r_conn)
        cards = data["cards"]
        cards.append({
            "name": character_loli,
            "attack": random.randint(1, 50),
            "defense": random.randint(1, 50)
        })
        await r.table("cardgame").get(str(ctx.author.id)).update({"cards": cards}).run(self.bot.r_conn)
        await ctx.send("Gave %s" % character_loli)

def setup(bot):
    bot.add_cog(CardGame(bot))