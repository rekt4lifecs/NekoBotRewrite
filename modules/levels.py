from discord.ext import commands
import discord, pymysql, config, time, random, math, datetime, requests, re, logging, aiomysql
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
from .utils import chat_formatting

log = logging.getLogger("NekoBot")

sqlCHAR = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f",
           "G", "g", "H", "h", "I", "i", "j", "J", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q",
           "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]

class Levels:
    """Levelling System OwO"""

    def __init__(self, bot):
        self.bot = bot

    async def database(self, datab: str, item: str, userid: int):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        db = await connection.cursor()
        try:
            await db.execute(f"SELECT {item} FROM {datab} WHERE userid = {userid}")
            return await db.fetchone()[0]
        except:
            return None

    async def usercheck(self, datab: str, userid: int):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        db = await connection.cursor()
        if not await db.execute(f'SELECT 1 FROM {datab} WHERE userid = {userid}'):
            return False
        else:
            return True

    @commands.command()
    async def profile(self, ctx, user : discord.Member = None):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        if user == None:
            user = ctx.message.author
        if await self.usercheck("levels", user.id) is False:
            return
        async with connection.cursor() as cur:
            await cur.execute(f"SELECT level FROM levels WHERE userid = {user.id}")
            levels = await cur.fetchone()
            levels = levels[0]
            await cur.execute(f"SELECT rep FROM levels WHERE userid = {user.id}")
            rep = await cur.fetchone()
            rep = rep[0]
            await cur.execute(f"SELECT title FROM levels WHERE userid = {user.id}")
            title = await cur.fetchone()
            title = title[0]
            await cur.execute(f"SELECT info FROM levels WHERE userid = {user.id}")
            desc = await cur.fetchone()
            desc = desc[0]
            if await self.usercheck("osu", user.id) is True:
                await cur.execute(f"SELECT osu FROM osu WHERE userid = {user.id}")
                osu = await cur.fetchone()
                osu = osu[0]
            else:
                osu = False
            if await self.usercheck("economy", user.id) is True:
                await cur.execute(f"SELECT balance FROM economy WHERE userid = {user.id}")
                balance = await cur.fetchone()
                balance = balance[0]
            else:
                balance = 0
        await ctx.trigger_typing()
        self._build_profile(user, title, desc, levels, balance, osu, rep)
        await ctx.send(file=discord.File(f"data/profiles/{user.id}.png"))

    @commands.command()
    async def settitle(self, ctx, *, title : str):
        """Set profile title"""
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        if await self.usercheck("levels", ctx.message.author.id) is False:
            await ctx.send("Error finding your profile.")
            return
        if '"' in title:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "'" in title:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif ";" in title:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        if len(title) > 24:
            await ctx.send("Your title is over 24 characters...")
            return
        try:
            async with connection.cursor() as cur:
                await cur.execute(f"UPDATE levels SET title = \"{title}\" WHERE userid = {ctx.message.author.id}")
                await connection.commit()
            await ctx.send("Title Updated!")
        except Exception as e:
            await ctx.send("Problem updating title to database...")

    @commands.command()
    async def setdesc(self, ctx, *, description : str):
        """Set profile description"""
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        if await self.usercheck("levels", ctx.message.author.id) is False:
            await ctx.send("Error finding your profile.")
            return
        if '"' in description:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif "'" in description:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        elif ";" in description:
            log.info(f"{ctx.message.author.id} {ctx.message.author.name} forbidden char")
            return
        if len(description) > 50:
            await ctx.send("Your description is too long.")
            return
        try:
            async with connection.cursor() as cur:
                await cur.execute(f"UPDATE levels SET info = \"{description}\" WHERE userid = {ctx.message.author.id}")
                await connection.commit()
            await ctx.send("Description Updated!")
        except Exception as e:
            await ctx.send("Problem updating description to database...")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def rep(self, ctx, user : discord.Member):
        """Rep a user."""
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        if user == ctx.message.author:
            await ctx.send("You can't rep yourself 😦")
            return
        elif user.bot is True:
            await ctx.send("You can't rep a bot 😦")
            return
        else:
            if await self.usercheck("levels", user.id) is False:
                await ctx.send("That user doesn't have an account yet")
                return
            async with connection.cursor() as cur:
                await cur.execute(f"SELECT lastrep FROM levels WHERE userid = {ctx.message.author.id}")
                getdb = await cur.fetchone()
                getdb = getdb[0]
            timenow = datetime.datetime.utcfromtimestamp(time.time()).strftime("%d")
            timecheck = datetime.datetime.utcfromtimestamp(int(getdb)).strftime("%d")
            if timecheck == timenow:
                await ctx.send("You already used your rep today 😦")
                return
            async with connection.cursor() as cur:
                await cur.execute("SELECT rep FROM levels WHERE userid = {}".format(user.id))
                rep_curr = await cur.fetchone()
                rep_curr = int(rep_curr[0])
                await cur.execute(f"UPDATE levels SET rep = {rep_curr + 1} WHERE userid = {user.id}")
                await connection.commit()
                await cur.execute(f"UPDATE levels SET lastrep = {int(time.time())} WHERE userid = {ctx.message.author.id}")
                await connection.commit()
            await ctx.send(f"{ctx.message.author.name} gave {user.mention} rep!")

    async def _get_user(self, id:int):
        users = set(self.bot.get_all_members())
        return discord.utils.get(users, id=id)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def top(self, ctx):
        """Show top of the top NekoBot users."""
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        async with connection.cursor() as cur:
            await cur.execute("SELECT userid, level FROM levels ORDER BY level DESC LIMIT 10")
            top_users = await cur.fetchall()
            print(top_users[0])
            user1 = await self._get_user(int(top_users[0][0]))
            user2 = await self._get_user(int(top_users[1][0]))
            user3 = await self._get_user(int(top_users[2][0]))
            topem = discord.Embed(color=0xDEADBF,
                                  title="Top Users",
                                  description=f"1. ♔**{user1}**♔ - **{self._find_level(int(top_users[0][1]))}** | ({int(top_users[0][0])})\n"
                                              f"2. ♕**{user2}**♕ - **{self._find_level(int(top_users[1][1]))}** | ({int(top_users[1][0])})\n"
                                              f"3. ♖**{user3}**♖ - **{self._find_level(int(top_users[2][1]))}** | ({int(top_users[2][0])})")
            await ctx.send(embed=topem)

    @commands.command()
    @commands.is_owner()
    async def setlvl(self, ctx, id: int, xp : int = 0):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        async with connection.cursor() as cur:
            await cur.execute(f"UPDATE levels SET level = {xp} WHERE userid = {id}")
            await connection.commit()
            await ctx.send(f"Set **{id}** to {xp}")

    @commands.command(aliases=['del'])
    @commands.is_owner()
    async def delete(self, ctx, id : int):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        async with connection.cursor() as cur:
            await cur.execute(f"DELETE FROM levels WHERE userid = {id}")
            await connection.commit()
            await ctx.send(f"Deleted {id}")
    # @commands.command()
    # @commands.is_owner()
    # async def imgbuild(self, ctx):
    #     """IMG Build"""
    #     user = ctx.message.author
    #     color = str(user.color).replace("#", "")
    #     fox = "The quick brown fox jumps over the lazy dog"
    #     self._build_profile(user, fox, fox, 5, 500, color, 500)
    #     await ctx.send(file=discord.File(f"data/imgwelcome/{user.id}.png"))
    #
    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, sql: str):
        """Inject SQL"""
        try:
            connection = await aiomysql.connect(user=config.db.user,
                                                password=config.db.password,
                                                host=config.db.host,
                                                port=config.db.port,
                                                db=config.db.database)
            async with connection.cursor() as cur:
                await cur.execute(sql)
                await connection.commit()
                await ctx.send("Done!")
        except Exception as e:
            await ctx.send(f"`{e}`")

    async def _handle_on_message(self, message):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        user = message.author
        if await self.usercheck("levels", user.id) is False:
            await self._create_user(user)
            return
        else:
            curr_time = time.time()
            async with connection.cursor() as cur:
                await cur.execute(f"SELECT lastxp FROM levels WHERE userid = {user.id}")
                lastxp = await cur.fetchone()
                if lastxp is None:
                    pass
                elif float(curr_time) - float(lastxp[0]) >= 120:
                    await self._process_exp(message, user.id, random.randint(15, 20))
                    await cur.execute(f"UPDATE levels SET lastxp = {time.time()} WHERE userid = {user.id}")
                    await connection.commit()

    async def _process_exp(self, message, userinfo, exp : int):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        async with connection.cursor() as cur:
            await cur.execute("SELECT level FROM levels WHERE userid = {}".format(userinfo))
            levels = await cur.fetchone()
            levels = levels[0]
            await cur.execute(f"UPDATE levels SET level = {levels + exp} WHERE userid = {userinfo}")
            await connection.commit()

    async def _give_chat_credit(self, user):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        async with connection.cursor() as cur:
            await cur.execute("select balance from economy where userid = {}".format(user.id))
            eco = await cur.fetchone()
            eco = int(eco[0])
            await cur.execute(f"UPDATE economy SET balance = {eco + 100} WHERE userid = {user.id}")
            await connection.commit()

    async def _create_user(self, user):
        connection = await aiomysql.connect(user=config.db.user,
                                            password=config.db.password,
                                            host=config.db.host,
                                            port=config.db.port,
                                            db=config.db.database)
        try:
            #userid, info, title, level, rep, lastxp,
            async with connection.cursor() as cur:
                await cur.execute(f"INSERT IGNORE INTO levels VALUES ({user.id}, info, title, 0, 0, 0, 0)")
                await connection.commit()
                log.info(f"Made account for {user.name} ({user.id})")
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

    def _hex_to_rgb(self, hex_num: str, a: int):
        h = hex_num.lstrip('#')

        # if only 3 characters are given
        if len(str(h)) == 3:
            expand = ''.join([x*2 for x in str(h)])
            h = expand

        colors = [int(h[i:i+2], 16) for i in (0, 2, 4)]
        colors.append(a)
        return tuple(colors)

    def _build_profile(self, user : discord.Member, title: str, desc: str, exp: int, balance: int, osu: str, rep: int):
        """V3"""
        desc_text = "\n".join(wrap(desc, 35))
        level = self._find_level(exp)
        if user.game is None:
            stats = "Chilling"
        else:
            stats = f"Playing {user.game}"
        if osu is not False:
            osu = f"OSU!: {osu}"
        else:
            osu = "OSU!: Not connected."
        created = user.created_at.strftime("%d %b %Y %H:%M")
        user_status = str(user.game).title()

        img = Image.open('data/backgrounds/default.png').convert('RGBA').resize((300, 300))
        box1 = Image.new('RGBA', (280, 200), (100, 100, 100, 100))
        box2 = Image.new('RGBA', (205, 50), (175, 175, 175, 140))
        box3 = Image.new('RGBA', (75, 170), (125, 125, 125, 175))
        box4 = Image.new('RGBA', (205, 200), (90, 90, 90, 150))

        avatar = user.avatar_url
        avatar = requests.get(avatar).content
        avatar = Image.open(BytesIO(avatar)).convert("RGBA").resize((75, 75))

        img.alpha_composite(box1, (10, 85))
        img.alpha_composite(box2, (85, 35))
        img.alpha_composite(box3, (10, 115))
        img.alpha_composite(box4, (85, 85))
        img.alpha_composite(avatar, (10, 10))

        draw = ImageDraw.Draw(img)
        title_txt = ImageFont.truetype("data/fonts/CaviarDreams.ttf", 20)
        user_txt = ImageFont.truetype("data/fonts/CaviarDreams.ttf", 17)
        side = ImageFont.truetype("data/fonts/CaviarDreams.ttf", 14)
        text1 = ImageFont.truetype("data/fonts/CaviarDreams.ttf", 12)
        text2 = ImageFont.truetype("data/fonts/CaviarDreams.ttf", 10)

        draw.text((90, 40), f"{title}", (9, 9, 9), font=title_txt)
        draw.text((90, 62), f"{user.name}#{user.discriminator}", (9, 9, 9), font=user_txt)
        draw.text((15, 85), f"Level: {level}", (9, 9, 9), font=side)
        draw.text((15, 97), f"Rep: {rep}", (9, 9, 9), font=side)

        draw.text((90, 90), f"Status: {user_status}", (255, 255, 255), font=text1)
        draw.text((90, 105), f"Created on {created}", (255, 255, 255), font=text1)
        draw.text((90, 120), f"${balance}", (255, 255, 255), font=text1)
        draw.text((90, 135), stats, (255, 255, 255), font=text1)
        draw.text((90, 150), osu, (255, 255, 255), font=text1)
        draw.text((90, 195), "Description:", (255, 255, 255), font=text2)
        draw.text((90, 207), desc_text, (255, 255, 255), font=text1)

        img.save(f"data/profiles/{user.id}.png")

    # def _build_profile(self, user, title : str, desc : str, rep : int, xp : int, color, balance : int, osu : bool):
    #     """v2 of build profile - ReKT#0001, Hex to RGB - stackoverflow.com"""
    #     darken = 20
    #     lighten = 20
    #
    #     level = self._find_level(xp)
    #     joined = user.created_at.strftime("%d %b %Y %H:%M")
    #     title = title.title()
    #     if len(title) > 22:
    #         title = title[:22] + "..."
    #     desc = "\n".join(wrap(desc, 35))
    #
    #     color = self._hex_to_rgb(color, 255)
    #     black = (0, 0, 0)
    #     white = (255, 255, 255)
    #
    #     if color[0] < 127 :
    #         top_color = (color[0] + lighten,
    #                      color[1] + lighten,
    #                      color[2] + lighten,
    #                      255)
    #         text_color = (255, 255, 255)
    #     else:
    #         top_color = (color[0] - darken,
    #                      color[1] - darken,
    #                      color[2] - darken,
    #                      255)
    #         text_color = (0, 0, 0)
    #
    #     if len(str(level)) > 1:
    #         level_len = (145, 125)
    #         level_text = (10, 90)
    #     else:
    #         level_len = (125, 125)
    #         level_text = (40, 90)
    #
    #     img = Image.new("RGBA", (362, 333), (225, 226, 225, 255))
    #     top_layer = Image.new('RGB', (362, 23), top_color)
    #     bar = Image.new('RGB', (362, 65), color)
    #     level_box = Image.new('RGB', level_len, (255, 255, 255))
    #     level_box_shadow = Image.new('RGBA', level_len, (64, 64, 64, 220))
    #
    #     draw = ImageDraw.Draw(img)
    #     text = ImageFont.truetype("data/fonts/material/Roboto-Light.ttf", 35)
    #     title_font = ImageFont.truetype("data/fonts/material/Roboto-Light.ttf", 25)
    #     unicode_font = ImageFont.truetype("data/fonts/unifont.ttf", 15)
    #     joined_font = ImageFont.truetype("data/fonts/material/Roboto-Light.ttf", 17)
    #     user_title = ImageFont.truetype("data/fonts/material/Roboto-Regular.ttf", 27)
    #     user_description = ImageFont.truetype("data/fonts/material/Roboto-Light.ttf", 20)
    #     level_font = ImageFont.truetype("data/fonts/material/Roboto-Thin.ttf", 125)
    #
    #     img.paste(top_layer, (0, 0))
    #     img.paste(bar, (0, 23))
    #     img.alpha_composite(level_box_shadow, (20, 110))
    #     img.paste(level_box, (10, 100))
    #
    #     osu_dest = (301, 25)
    #
    #     if osu is True:
    #         draw.text((300, 25), "OSU: ✓", text_color, font=unicode_font)
    #     else:
    #         draw.text((300, 25), "OSU: ✖", text_color, font=unicode_font)
    #
    #     draw.text((15, 32), f"{user.name + '#' + user.discriminator}", text_color, font=text)
    #     # draw.text((20, 105), "Level", black, font=title)
    #     draw.text((165, 120), f"{rep} Rep", black, font=title_font)
    #     draw.text((165, 150), f"${balance}", black, font=title_font)
    #     draw.text((165, 185), f"Joined on\n{joined}", black, font=joined_font)
    #     draw.text((10, 240), str(title), black, font=user_title)
    #     draw.text((10, 270), str(desc), black, font=user_description)
    #     draw.text(level_text, str(level), black, font=level_font)
    #
    #     img.save(f"data/profiles/{user.id}.png")

    # def _build_profile(self, user, title : str, desc : str, rep : int, xp : int):
    #     img = Image.new('RGBA', (300, 300), (255, 255, 255, 255))
    #     bg = Image.open("data/backgrounds/default.jpg").resize((300, 300))
    #     titlebg = Image.new('RGBA', (187, 25), (100, 100, 100, 130))
    #     badgebg = Image.new('RGBA', (100, 160), (80, 80, 80, 140))
    #     descbg = Image.new('RGBA', (178, 170), (100, 100, 100, 130))
    #     layer1 = Image.new('RGBA', (290, 180), (130, 130, 130, 130))
    #     avatar = user.avatar_url
    #     avatar = requests.get(avatar).content
    #     avatar = Image.open(BytesIO(avatar)).convert("RGBA").resize((90, 90))
    #
    #     img.paste(bg)
    #     img.alpha_composite(titlebg, (105, 95))
    #     img.alpha_composite(layer1, (5, 120))
    #     img.alpha_composite(badgebg, (10, 135))
    #     img.alpha_composite(descbg, (110, 125))
    #     img.paste(avatar, (15, 60))
    #
    #     draw = ImageDraw.Draw(img)
    #     titlet = ImageFont.truetype("data/fonts/win10/corbel.ttf", 16)
    #     rept = ImageFont.truetype("data/fonts/win10/verdana.ttf", 15)
    #     desct = ImageFont.truetype("data/fonts/win10/lucon.ttf", 13)
    #     levelt = ImageFont.truetype("data/fonts/win10/courbd.ttf", 40)
    #     leveltt = ImageFont.truetype("data/fonts/win10/courbd.ttf", 20)
    #     font1 = ImageFont.truetype("data/fonts/win10/courbd.ttf", 12)
    #
    #     desc = "\n".join(wrap(desc, 22))
    #     level = self._find_level(xp)
    #
    #     draw.text((115, 100), title[:24], (255, 255, 255), font=titlet)
    #     draw.text((30, 155), f"Rep: {rep}", (255, 255, 255), font=rept)
    #     draw.line(((130, 220), (267, 220)), (200, 200, 200), 1)
    #     draw.text((120, 230), desc, (255, 255, 255), font=desct)
    #     draw.text((180, 150), str(level), (255, 255, 255), font=levelt)
    #     draw.text((160, 190), "LEVEL", (255, 255, 255), font=leveltt)
    #     draw.text((120, 130), f"{user.name}", (255, 255, 255), font=font1)
    #     draw.text((120, 145), f"XP: {xp}", (255, 255, 255), font=font1)
    #     print(f"Built profile {user.name} ({user.id})")
    #     img.save(f"data/profiles/{user.id}.png")

def setup(bot):
    n = Levels(bot)
    bot.add_listener(n._handle_on_message, "on_message")
    bot.add_cog(n)