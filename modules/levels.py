from discord.ext import commands
import discord, pymysql, config, time, random, math, datetime, requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
from .utils import chat_formatting

connection = pymysql.connect(user=config.db.user,
                             password=config.db.password,
                             host=config.db.host,
                             port=config.db.port,
                             database=config.db.database)
db = connection.cursor()

class Levels:
    """Levelling System OwO"""

    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def profile(self, ctx, user : discord.Member = None):
    #     if user == None:
    #         user = ctx.message.author
    #     db.execute("SELECT level FROM levels WHERE userid = {}".format(user.id))
    #     levels = db.fetchone()[0]
    #     db.execute("SELECT rep FROM levels WHERE userid = {}".format(user.id))
    #     REP = db.fetchone()[0]
    #
    #     try:
    #         db.execute("select balance from economy where userid = {}".format(user.id))
    #         balance = db.fetchone()[0]
    #     except:
    #         balance = 0
    #
    #     embed = discord.Embed(color=0xDEADBF)
    #     embed.set_author(name=f"{user.name}")
    #     embed.set_thumbnail(url=user.avatar_url)
    #     embed.add_field(name="Level", value=f"**{self._find_level(levels)}**")
    #     embed.add_field(name="Rep", value=f"**{REP}**")
    #     embed.add_field(name="Balance", value=f"{balance}")
    #     embed.set_footer(text=f"Total XP: {levels}, {self._level_exp(self._find_level(levels))}/{self._required_exp(self._find_level(levels))}")
    #
    #     await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def profile(self, ctx, user : discord.Member = None):
        """Get a users profile."""
        if user == None:
            user = ctx.message.author
        try:
            db.execute("SELECT level FROM levels WHERE userid = {}".format(user.id))
            levels = db.fetchone()[0]
            db.execute("SELECT info FROM levels WHERE userid = {}".format(user.id))
            desc = db.fetchone()[0]
            db.execute("SELECT title FROM levels WHERE userid = {}".format(user.id))
            title = db.fetchone()[0]
            db.execute("SELECT rep FROM levels WHERE userid = {}".format(user.id))
            rep = db.fetchone()[0]
        except:
            levels = 0
            title = ""
            desc = ""
            rep = 0
        self._build_profile(user, title, desc, rep, levels)
        await ctx.send(file=discord.File(f"data/profiles/{user.id}.png"))

    @commands.command()
    async def settitle(self, ctx, title : str):
        """Set profile title"""
        if not db.execute('SELECT 1 FROM levels WHERE userid = {}'.format(ctx.message.author.id)):
            await ctx.send("Error finding your profile.")
            return
        if len(title) > 24:
            await ctx.send("Your title is over 24 characters...")
            return
        try:
            db.execute(f"UPDATE levels SET title = \"{title}\" WHERE userid = {ctx.message.author.id}")
            connection.commit()
            await ctx.send("Title Updated!")
        except Exception as e:
            await ctx.send("Problem updating title to database...\n`{}`".format(e))

    @commands.command()
    async def setdesc(self, ctx, description : str):
        """Set profile description"""
        if not db.execute('SELECT 1 FROM levels WHERE userid = {}'.format(ctx.message.author.id)):
            await ctx.send("Error finding your profile.")
            return
        if len(description) > 50:
            await ctx.send("Your description is too long.")
            return
        try:
            db.execute(f"UPDATE levels SET info = \"{description}\" WHERE userid = {ctx.message.author.id}")
            connection.commit()
            await ctx.send("Description Updated!")
        except Exception as e:
            await ctx.send("Problem updating description to database...\n`{}`".format(e))

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def rep(self, ctx, user : discord.Member):
        """Rep a user."""
        if user == ctx.message.author:
            await ctx.send("You can't rep yourself 😦")
            return
        elif user == user.bot:
            await ctx.send("You can't rep a bot 😦")
            return
        else:
            if not db.execute('SELECT 1 FROM levels WHERE userid = {}'.format(user.id)):
                await ctx.send("That user doesn't have an account yet")
                return
            db.execute(f"SELECT lastrep FROM levels WHERE userid = {ctx.message.author.id}")
            getdb = db.fetchone()[0]
            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(int(getdb)).strftime("%d")
            if timecheck == timenow:
                await ctx.send("You already used your rep today 😦")
                return
            db.execute("SELECT rep FROM levels WHERE userid = {}".format(user.id))
            rep_curr = int(db.fetchone()[0])
            db.execute(f"UPDATE levels SET rep = {rep_curr + 1} WHERE userid = {user.id}")
            connection.commit()
            db.execute(f"UPDATE levels SET lastrep = {int(time.time())} WHERE userid = {ctx.message.author.id}")
            connection.commit()
            await ctx.send(f"{ctx.message.author.name} gave {user.mention} rep!")

    async def _handle_on_message(self, message):
        user = message.author
        text = message.content
        userinfo = user.id
        await self._create_user(user)
        curr_time = time.time()
        db.execute(f"SELECT lastxp FROM levels WHERE userid = {user.id}")
        if float(curr_time) - float(db.fetchone()[0]) >= 120:
            await self._process_exp(message, userinfo, random.randint(15, 20))
            #await self._give_chat_credit(user)
            db.execute(f"UPDATE levels SET lastxp = {time.time()} WHERE userid = {userinfo}")
            connection.commit()

    async def _process_exp(self, message, userinfo, exp : int):
        db.execute("SELECT level FROM levels WHERE userid = {}".format(userinfo))
        levels = db.fetchone()[0]
        db.execute(f"UPDATE levels SET level = {levels + exp} WHERE userid = {userinfo}")
        connection.commit()

    # async def _give_chat_credit(self, user):
    #     db.execute("select balance from economy where userid = {}".format(user.id))
    #     eco = int(db.fetchone())
    #     db.execute(f"UPDATE economy SET balance = {eco + 100} WHERE userid = {user.id}")
    #     connection.commit()

    async def _create_user(self, user):
        try:
            if not db.execute('SELECT 1 FROM levels WHERE userid = {}'.format(user.id)):
                #userid, info, title, level, rep, lastxp, lastrep
                db.execute(f"INSERT IGNORE INTO levels VALUES ({user.id}, info, title, 0, 0, 0, 0)")
                connection.commit()
                print(f"Made account for {user.name} ({user.id})")
            else:
                pass
        except AttributeError:
            pass

    def _required_exp(self, level: int):
        if level < 0:
            return 0
        return 139 * level + 65

    def _level_exp(self, level: int):
        return level * 65 + 139 * level * (level - 1) // 2

    def _find_level(self, total_exp):
        # this is specific to the function above
        return int((1 / 278) * (9 + math.sqrt(81 + 1112 * (total_exp))))

    def _build_profile(self, user, title : str, desc : str, rep : int, xp : int):
        img = Image.new('RGBA', (300, 300), (255, 255, 255, 255))
        bg = Image.open("data/backgrounds/default.jpg").resize((300, 300))
        titlebg = Image.new('RGBA', (187, 25), (100, 100, 100, 130))
        badgebg = Image.new('RGBA', (100, 160), (80, 80, 80, 140))
        descbg = Image.new('RGBA', (178, 170), (100, 100, 100, 130))
        layer1 = Image.new('RGBA', (290, 180), (130, 130, 130, 130))
        avatar = user.avatar_url
        avatar = requests.get(avatar).content
        avatar = Image.open(BytesIO(avatar)).convert("RGBA").resize((90, 90))

        img.paste(bg)
        img.alpha_composite(titlebg, (105, 95))
        img.alpha_composite(layer1, (5, 120))
        img.alpha_composite(badgebg, (10, 135))
        img.alpha_composite(descbg, (110, 125))
        img.paste(avatar, (15, 60))

        draw = ImageDraw.Draw(img)
        titlet = ImageFont.truetype("data/fonts/win10/corbel.ttf", 16)
        rept = ImageFont.truetype("data/fonts/win10/verdana.ttf", 15)
        desct = ImageFont.truetype("data/fonts/win10/lucon.ttf", 13)
        levelt = ImageFont.truetype("data/fonts/win10/courbd.ttf", 40)
        leveltt = ImageFont.truetype("data/fonts/win10/courbd.ttf", 20)
        font1 = ImageFont.truetype("data/fonts/win10/courbd.ttf", 12)

        desc = "\n".join(wrap(desc, 22))
        level = self._find_level(xp)

        draw.text((115, 100), title[:24], (255, 255, 255), font=titlet)
        draw.text((30, 155), f"Rep: {rep}", (255, 255, 255), font=rept)
        draw.line(((130, 220), (267, 220)), (200, 200, 200), 1)
        draw.text((120, 230), desc, (255, 255, 255), font=desct)
        draw.text((180, 150), str(level), (255, 255, 255), font=levelt)
        draw.text((160, 190), "LEVEL", (255, 255, 255), font=leveltt)
        draw.text((120, 130), f"{user.name}", (255, 255, 255), font=font1)
        draw.text((120, 145), f"XP: {xp}", (255, 255, 255), font=font1)
        print(f"Built profile {user.name} ({user.id})")
        img.save(f"data/profiles/{user.id}.png")

def setup(bot):
    n = Levels(bot)
    bot.add_listener(n._handle_on_message, "on_message")
    bot.add_cog(n)