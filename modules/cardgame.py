import discord, random, time, datetime, asyncio
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import textwrap
import aiohttp
import rethinkdb as r
import os
from prettytable import PrettyTable
import gettext
from io import BytesIO

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
    "Fear Kubrick",
    "Sengoku Nadeko",
    "Kirima Sharo",
    "Noumi Kudryavka",
    "Kanna",
    "chifuyu_himeki",
    "holo",
    "dva",
    "megumin",
    "Halloween NekoBot" # Special Halloween Card hahayes
] # "Louise Francoise Le Blanc De La Valliere",
  # "Hoshimiya Kate",

class CardGame:
    """Loli Card Gamelol xDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"""

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("cardgame", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

    async def __post_to_hook(self, action:str, user:discord.Member, amount):
        try:
            async with aiohttp.ClientSession() as cs:
                await cs.post("http://localhost:1241", json={
                    "user": str(user.id),
                    "action": action,
                    "amount": amount,
                    "time": str(int(time.time()))
                })
        except:
            pass

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
        _ = await self._get_text(ctx)

        await self.__check_for_user(ctx.author.id)

        if ctx.invoked_subcommand is None:
            return await ctx.send(_("A loli roleplaying card game ofc!\n\n"
                                    "**Commands**\n"
                                    "**n!card daily** - Get your daily cards\n"
                                    "**n!card display** - Display a card of yours\n"
                                    "**n!card list** - Lists your cards\n"
                                    "**n!card sell** - Sell a card\n"
                                    "**n!card transfer** - Transfer Cards"))

    @card.command(name="transfer")
    async def card_transfer(self, ctx, card_number, user:discord.Member):
        """Transfer cards to other users"""
        _ = await self._get_text(ctx)

        if user == ctx.author:
            return await ctx.send(_("You can't send yourself cards"))
        elif user.bot:
            return await ctx.send(_("You can't send bots cards."))

        try:
            card_number = int(card_number)
        except:
            return await ctx.send(_("Not a valid number"))

        if card_number > 6 or card_number <= 0:
            return await ctx.send(_("Not a valid card number."))

        await self.__check_for_user(ctx.author.id)
        await self.__check_for_user(user.id)

        author_data = await r.table("cardgame").get(str(ctx.author.id)).run(self.bot.r_conn)
        author_cards = author_data["cards"]
        user_data = await r.table("cardgame").get(str(user.id)).run(self.bot.r_conn)
        user_cards = user_data["cards"]

        if len(user_cards) >= 6:
            return await ctx.send(_("%s has no slots left") % user.mention)

        try:
            card = author_cards[card_number-1]
        except:
            return await ctx.send(_("Not a valid card."))

        user_cards.append(card)

        newdata = {
            "cards": user_cards
        }

        await r.table("cardgame").get(str(ctx.author.id)).update({"cards": r.row["cards"].delete_at(card_number-1)}).run(self.bot.r_conn)
        await r.table("cardgame").get(str(user.id)).update(newdata).run(self.bot.r_conn)
        await ctx.send(_("Transferred card to %s!") % user.mention)

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
        _ = await self._get_text(ctx)

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
            return await ctx.send(_("Wait another %sh %sm before using daily again...") % (h, m,))

        if len(cards) >= 6:
            return await ctx.send(_("All of your slots are full ;w;"))

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
        await ctx.send(_("Given character **%s!**") % character_loli.replace('_', ' ').title())

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
        elif character == "hibiki":
            description = "Qtiest qt of all qts"
        else:
            description = ""

        draw.text((37, 23), character.replace('_', ' '), (0, 0, 0), title_font)
        draw.text((255, 550), str(attack), (0, 0, 0), lower_font)
        draw.text((344, 550), str(defense), (0, 0, 0), lower_font)
        draw.text((40, 477), textwrap.fill(description, 37), (0, 0, 0), font=desc_font)

        img.save(f"data/cards/{num}.png")  # there is a thing called BytesIO oldme smh todo

    @card.command(name='sell')
    async def card_sell(self, ctx, num: int):
        """Sell a card"""
        _ = await self._get_text(ctx)

        await self.__check_for_user(ctx.author.id)
        if num > 6 or num < 1:
            return await ctx.send(_("**Out of card range.**"))

        author = ctx.author
        data = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        if not await r.table("economy").get(str(author.id)).run(self.bot.r_conn):
            return await ctx.send(_("❌ | **You don't have a bank account to sell your cards, make one with `n!register`**"))

        try:
            card = cards[num-1]
        except:
            return await ctx.send(_("No cards in this slot..."))

        cardname = card["name"]
        cardname_en = str(cardname).replace('_', ' ').title()
        attack = card["attack"]
        defense = card["defense"]

        cardprice = int(random.randint(10000, 15000) + (((attack * .25) + (defense * .25)) * 1000))

        await ctx.send(_("%s, type `yes` to sell **%s** for %s") % (author.mention, cardname_en, cardprice))

        def check(m):
            return m.channel == ctx.message.channel and m.author == author

        try:
            x = await self.bot.wait_for('message', check=check, timeout=15.0)
            if not str(x.content).lower() == "yes":
                return await ctx.send(_("❌ | **Cancelled Transaction.**"))
        except asyncio.TimeoutError:
            await ctx.send(_("❌ | **Cancelled Transaction.**"))
            return

        after_check = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
        if after_check != data:
            await self.__post_to_hook("Card Sell Fail 😤😤", author, 0)
            return await ctx.send(_("Card has already been sold"))

        await r.table("cardgame").get(str(author.id)).update({"cards": r.row["cards"].delete_at(num-1)}).run(self.bot.r_conn)
        economy = await r.table("economy").get(str(author.id)).run(self.bot.r_conn)
        await r.table("economy").get(str(author.id)).update({"balance": economy["balance"] + cardprice}).run(self.bot.r_conn)

        await ctx.send(_("Sold %s for %s") % (cardname_en, cardprice))
        await self.__post_to_hook("Sold card", author, cardprice)

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
                table.add_row([displaynum, card["name"].replace("_", " ").title(), card["attack"], card["defense"]])
            except:
                table.add_row([displaynum, "Empty", "0", "0"])

            cardnum += 1
            displaynum += 1

        await ctx.send("```\n%s\n```" % table)

    @card.command(name="display", aliases=["show"])
    async def card_display(self, ctx, num: int):
        """Display your card(s)"""
        await ctx.trigger_typing()
        _ = await self._get_text(ctx)
        await self.__check_for_user(ctx.author.id)
        if num > 6 or num < 1:
            return await ctx.send(_("**Out of card range.**"))

        data = await r.table("cardgame").get(str(ctx.author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        try:
            card = cards[num-1]
        except:
            return await ctx.send(_("Empty Slot..."))

        num = ctx.author.id

        character_name = card["name"]
        character_name_en = str(character_name).replace('_', ' ').title()
        attack = card["attack"]
        defense = card["defense"]
        self._generate_card(character_name, num, attack, defense)

        embed = discord.Embed(color=0xDEADBF, title=character_name_en)
        embed.add_field(name=_("Attack"), value=str(attack))
        embed.add_field(name=_("Defense"), value=str(defense))

        await ctx.send(file=discord.File(f'data/cards/{num}.png'), embed=embed.set_image(url=f'attachment://{num}.png'))
        os.remove("data/cards/%s.png" % num)  # smh

    @card.command(name='generate', hidden=True)
    @commands.is_owner()
    async def card_gen(self, ctx, character: str = "shiro", attack: int = 1, defense: int = 1):
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

        temp = BytesIO()
        img.save(temp, format="png")
        temp.seek(0)
        await ctx.send(file=discord.File(fp=temp, filename="generated.png"),
                       embed=discord.Embed(color=0xDEADBF).set_image(url=f'attachment://generated.png'))

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