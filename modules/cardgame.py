import discord, random, time, datetime, asyncio
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import textwrap
import rethinkdb as r
from prettytable import PrettyTable
from io import BytesIO

list_ = [
    "Aoba Suzukaze",
    "Dola Schwi",
    "Isla",
    "Rory Mercury",
    "Sora Ginko",
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
    "megumin"
]

class CardGame(commands.Cog):

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
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def card(self, ctx: commands.Context):
        """Loli Card Game OwO"""

        await self.__check_for_user(ctx.author.id)

        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

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

        if card_number not in range(1, 13):
            return await ctx.send("Not a valid card number.")

        await self.__check_for_user(ctx.author.id)
        await self.__check_for_user(user.id)

        author_data = await r.table("cardgame").get(str(ctx.author.id)).run(self.bot.r_conn)
        author_cards = author_data["cards"]
        user_data = await r.table("cardgame").get(str(user.id)).run(self.bot.r_conn)
        user_cards = user_data["cards"]

        if len(user_cards) >= 12:
            return await ctx.send("{} has no slots left".format(user.mention))

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
        await ctx.send("Transferred card to {}!".format(user.mention))

    @card.command(name='daily')
    async def card_daily(self, ctx):
        """Get your card daily"""

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
            return await ctx.send("Wait another {}h {}m before using daily again...".format(h, m,))

        if len(cards) >= 12:
            return await ctx.send("All of your slots are full ;w;")

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
        await ctx.send("Given character **{}!**".format(character_loli.replace('_', ' ').title()))

    def _generate_card(self, character: str, attack: int, defense: int):
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

        temp = BytesIO()
        img.save(temp, format="jpeg")
        temp.seek(0)

        img.close()
        return temp

    @card.command(name='sell')
    async def card_sell(self, ctx, num: int):
        """Sell a card"""

        await self.__check_for_user(ctx.author.id)
        if num not in range(1, 13):
            return await ctx.send("**Out of card range.**")

        author = ctx.author
        data = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        if not await r.table("economy").get(str(author.id)).run(self.bot.r_conn):
            return await ctx.send("❌ | **You don't have a bank account to sell your cards, make one with `n!register`**")

        try:
            card = cards[num-1]
        except:
            return await ctx.send("No cards in this slot...")

        cardname = card["name"]
        cardname_en = str(cardname).replace('_', ' ').title()
        attack = card["attack"]
        defense = card["defense"]

        cardprice = int(random.randint(10000, 15000) + (((attack * .25) + (defense * .25)) * 1000))

        await ctx.send("{}, type `yes` to sell **{}** for {}".format(author.mention, cardname_en, "￥{:,}".format(cardprice)))

        def check(m):
            return m.channel == ctx.message.channel and m.author == author

        try:
            x = await self.bot.wait_for("message", check=check, timeout=15.0)
            if not str(x.content).lower() == "yes":
                return await ctx.send("❌ | **Cancelled Transaction.**")
        except asyncio.TimeoutError:
            await ctx.send("❌ | **Cancelled Transaction.**")
            return

        after_check = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
        if after_check != data:
            return await ctx.send("Card has already been sold")

        await r.table("cardgame").get(str(author.id)).update({"cards": r.row["cards"].delete_at(num-1)}).run(self.bot.r_conn)
        economy = await r.table("economy").get(str(author.id)).run(self.bot.r_conn)
        await r.table("economy").get(str(author.id)).update({"balance": economy["balance"] + cardprice}).run(self.bot.r_conn)

        await ctx.send("Sold {} for {}".format(cardname_en, "￥{:,}".format(cardprice)))

    @card.command(name='list')
    async def card_list(self, ctx):
        """List your cards"""
        await self.__check_for_user(ctx.author.id)
        author = ctx.message.author

        data = await r.table("cardgame").get(str(author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        table = PrettyTable()
        table.field_names = ["Number", "Card", "Attack", "Defense"]

        for i, x in enumerate(range(12)):
            try:
                card = cards[i]
                table.add_row([i + 1, card["name"].replace("_", " ").title(), card["attack"], card["defense"]])
            except:
                table.add_row([i + 1, "Empty", "0", "0"])

        await ctx.send("```\n{}\n```".format(table))

    @card.command(name="display", aliases=["show"])
    async def card_display(self, ctx, num: int):
        """Display your card(s)"""
        await ctx.trigger_typing()
        await self.__check_for_user(ctx.author.id)
        if num not in range(1, 13):
            return await ctx.send("**Out of card range.**")

        data = await r.table("cardgame").get(str(ctx.author.id)).run(self.bot.r_conn)
        cards = data["cards"]

        try:
            card = cards[num-1]
        except:
            return await ctx.send("Empty Slot...")

        character_name = card["name"]
        character_name_en = str(character_name).replace('_', ' ').title()
        attack = card["attack"]
        defense = card["defense"]

        embed = discord.Embed(color=0xDEADBF, title=character_name_en)
        embed.add_field(name="Attack", value=str(attack))
        embed.add_field(name="Defense", value=str(defense))

        await ctx.send(file=discord.File(self._generate_card(character_name, attack, defense), filename="image.jpg"), embed=embed.set_image(url="attachment://image.jpg"))

def setup(bot):
    bot.add_cog(CardGame(bot))
