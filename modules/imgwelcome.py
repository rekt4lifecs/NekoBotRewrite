from discord.ext import commands
import discord, config, aiohttp
from io import BytesIO
from .utils import checks
from PIL import Image, ImageFont, ImageDraw
import string
import aiomysql

class IMGWelcome:
    """IMGWelcome"""

    def __init__(self, bot):
        self.bot = bot

    def forbiddencheck(self, text:str):
        characters = string.ascii_letters + string.digits + " "
        forbidden_char = 0
        for letter in text:
            if letter not in characters:
                forbidden_char += 1
        return forbidden_char

    async def execute(self, query: str, isSelect: bool = False, fetchAll: bool = False, commit: bool = False):
        connection = await aiomysql.connect(host='localhost', port=3306,
                                              user='root', password=config.dbpass,
                                              db='nekobot')
        async with connection.cursor() as db:
            await db.execute(query)
            if isSelect:
                if fetchAll:
                    values = await db.fetchall()
                else:
                    values = await db.fetchone()
            if commit:
                await connection.commit()
        if isSelect:
            return values

    @commands.command()
    @checks.is_admin()
    async def imgwelcome(self, ctx):
        embed = discord.Embed(color=0xDEABDF,
                              title="IMGWelcomer")
        embed.add_field(name="Instructions", value="Set your channel with **imgchannel**,\n"
                                                   "Step 2: Set your content with **imgcontent** such as \"Welcome user To server\",\n"
                                                   "Step 3: Change your background with **imgbg**\n"
                                                   "Step 4: Profit?!\n\n"
                                                   "To remove the welcomer use `n!imgdelete`.")
        await ctx.send(embed=embed)
        if not await self.execute('SELECT 1 FROM imgwelcome WHERE server = {}'.format(ctx.message.guild.id),
                                  isSelect=True):
            username = "0 1"
            username.find("0")
            await self.execute(f"INSERT IGNORE INTO imgwelcome VALUES ({ctx.message.guild.id}, \"Welcome user to server!!!\", \"NONE\", \"arial.ttf\", \"NONE\")", commit=True)
            print(f"Added {ctx.message.guild.name} ({ctx.message.guild.id})")

    @commands.command()
    @checks.is_admin()
    async def imgchannel(self, ctx, channel : discord.TextChannel):
        """Select a IMG Welcoming text channel"""
        if not await self.execute('SELECT 1 FROM imgwelcome WHERE server = {}'.format(ctx.message.guild.id),
                                  isSelect=True):
            await ctx.send("Use `imgwelcome` to initialize.")
            return
        else:
            await self.execute(f"UPDATE imgwelcome SET channel = \"{channel.id}\" WHERE server = {ctx.message.guild.id}",
                               commit=True)
            await ctx.send(f"Updated imgwelcome to {channel.name}")
            print(f"UPDATED {ctx.message.guild.name} ({ctx.message.guild.id}) - Channel to {channel.name} ({channel.id})")

    @commands.command()
    @checks.is_admin()
    async def imgdelete(self, ctx):
        """Remove imgwelcomer from the server."""
        if not await self.execute('SELECT 1 FROM imgwelcome WHERE server = {}'.format(ctx.message.guild.id),
                                  isSelect=True):
            await ctx.send("Use `imgwelcome` to initialize.")
            return
        else:
            await self.execute(f"DELETE FROM imgwelcome WHERE server = {ctx.message.guild.id}", commit=True)
            await ctx.send(f"Removed imgwelcome!")

    @commands.command()
    @checks.is_admin()
    async def imgcontent(self, ctx, content:str=None):
        if content == None:
            content = "Welcome user to server"
            await ctx.send('Content reset to default "Welcome user to server"')
        else:
            if not await self.execute('SELECT 1 FROM imgwelcome WHERE server = {}'.format(ctx.message.guild.id),
                                      isSelect=True):
                await ctx.send("Use `imgwelcome` to initialize.")
                return
            await ctx.send(f"Updated content to {content}")
        await self.execute(f"UPDATE imgwelcome SET content = \"{content}\" WHERE server = {ctx.message.guild.id}",
                           commit=True)
        print(f"UPDATED {ctx.message.guild.name} ({ctx.message.guild.id}) - Content to {content}")

    @commands.command()
    @checks.is_admin()
    async def imgbg(self, ctx, img : str = ""):
        """Change image BG, Image must be 500x150."""
        if not await self.execute('SELECT 1 FROM imgwelcome WHERE server = {}'.format(ctx.message.guild.id),
                          isSelect=True):
            await ctx.send("Use `imgwelcome` to initialize.")
            return
        if img == "":
            await self.execute(f"UPDATE imgwelcome SET background = \"NONE\" WHERE server = {ctx.message.guild.id}",
                       commit=True)
            await ctx.send("Reset to default.")
            return
        if img.startswith("http") and img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith(".png"):
            async with aiohttp.ClientSession() as cs:
                async with cs.get(img) as r:
                    status = r.status
            if status == 200:
                await self.execute(f"UPDATE imgwelcome SET background = \"{img}\" WHERE server = {ctx.message.guild.id}",
                           commit=True)
                await ctx.send(f"Updated background to `{img}`")
                print(f"UPDATED {ctx.message.guild.name} ({ctx.message.guild.id}) - BG to {img}")
            else:
                await ctx.send("Can't get that website.")
        else:
            await ctx.send("That is not a valid Image URL")

    async def on_member_join(self, member):
        try:
            server = member.guild
            if not await self.execute('SELECT 1 FROM imgwelcome WHERE server = {}'.format(server.id),
                              isSelect=True):
                return
            channel = await self.execute("SELECT channel FROM imgwelcome WHERE server = {}".format(server.id),
                               isSelect=True)
            channel = channel[0]
            bg = await self.execute("SELECT background FROM imgwelcome WHERE server = {}".format(server.id),
                                    isSelect=True)
            bg = bg[0]
            content = await self.execute("SELECT content FROM imgwelcome WHERE server = {}".format(server.id),
                       isSelect=True)
            content = content[0]
            await self._build_member_join(member, channel, bg, content, server)
            chan = self.bot.get_channel(int(channel))
            content = str(content).replace("user", f"{member.mention}").replace("server", f"{member.guild}")
            await chan.send(file=discord.File(f"data/imgwelcome/{server.id}.png"), content=content)
            #await ctx.send(file=discord.File(f"data/img/{server.id}.png"))
        except: pass

    async def _build_member_join(self, user, channel, bg, content, server):
        if bg == "NONE":
            bg = Image.new('RGB', (500, 150), (255, 255, 255))
        else:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(bg) as r:
                    background = await r.read()
            bg = Image.open(BytesIO(background))

        async with aiohttp.ClientSession() as cs:
            async with cs.get(user.avatar_url) as r:
                avatardata = await r.read()
        avatar = Image.open(BytesIO(avatardata))

        welcome_font = ImageFont.truetype("data/fonts/CaviarDreams.ttf", 40)
        name_font = ImageFont.truetype("data/fonts/CaviarDreams_Bold.ttf", 45)
        server_font = ImageFont.truetype("data/fonts/CaviarDreams.ttf", 35)
        server_name = ImageFont.truetype("data/fonts/CaviarDreams_Bold.ttf", 35)

        draw = ImageDraw.Draw(bg)

        if len(user.name) > 10:
            name_font = ImageFont.truetype("data/fonts/CaviarDreams_Bold.ttf", 35)

        bg.paste(avatar.resize((150, 150)), (0, 0))
        draw.text((160, 10), f"Welcome", (32, 32, 32), font=welcome_font)
        draw.text((160, 50), f"{user.name}", (0, 0, 0), font=name_font)
        draw.text((160, 95), f"to", (32, 32, 32), font=server_font)
        draw.text((210, 95), f"{server.name}", (0, 0, 0), font=server_name)

        bg.save(f"data/imgwelcome/{server.id}.png")

    def _get_suffix(self, num):
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 10 <= num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = suffixes.get(num % 10, 'th')
        return suffix

    async def _circle_border(self, circle_img_size: tuple):
        border_size = []
        for i in range(len(circle_img_size)):
            border_size.append(circle_img_size[0] + 8)
        return tuple(border_size)

def setup(bot):
    bot.add_cog(IMGWelcome(bot))