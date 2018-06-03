from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import discord, os, aiohttp, string
from io import BytesIO

class IMGWelcome:

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def imgwelcome(self, ctx):
        """IMG Welcomer"""
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if not await db.execute(f"SELECT 1 FROM newimgwelcome WHERE server = {ctx.message.guild.id}"):
                    content = "Welcome {0} to {1}!"
                    await db.execute(f"INSERT INTO newimgwelcome VALUES ({ctx.message.guild.id}, {ctx.message.channel.id}, \"{content}\")")
        if ctx.invoked_subcommand is None:
            em = discord.Embed(color=0xDEADBF, title="IMG Welcomer",
                               description="**n!imgwelcome img** - Set the background image\n"
                                           "**n!imgwelcome text** - Change the Welcome text above the image.\n"
                                           "**n!imgwelcome channel** - Set the welcome channel.\n"
                                           "**n!imgwelcome disable** - Remove it from your server.")
            await ctx.send(embed=em)

    @imgwelcome.command(name="disable")
    async def img_disable(self, ctx):
        """Disable imgwelcome"""
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(f"DELETE FROM newimgwelcome WHERE server = {ctx.message.guild.id}")
        await ctx.send("Disabled imgwelcome...")

    @imgwelcome.command(name="channel")
    async def img_channel(self, ctx, channel:discord.TextChannel):
        """Set the img text channel"""
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(f"UPDATE newimgwelcome SET channel = {channel.id} WHERE server = {ctx.message.guild.id}")
        await ctx.send(f"Updated channel to {channel.name}")

    @imgwelcome.command(name="img")
    async def img_img(self, ctx):
        """Set the background welcome image"""
        await ctx.send("Send an image or type anything without sending an image to reset back to default.")

        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        msg = await self.bot.wait_for('message', check=check)

        if len(msg.attachments) >= 1:
            attachment = str(msg.attachments[0].url).rpartition(".")[2]
            if attachment.lower() not in ["png", "jpg", "jpeg", "gif"]:
                return await ctx.send("Not a valid image type <:bakaa:432914537608380419>")
            if os.path.exists(f"data/imgwelcome/{ctx.message.guild.id}.png"):
                os.remove(f"data/imgwelcome/{ctx.message.guild.id}.png")
            try:
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(msg.attachments[0].url) as r:
                        imgdata = await r.read()
                img = Image.open(BytesIO(imgdata)).convert("RGBA").resize((500, 150))
                bg = Image.new("RGBA", (500, 150), (0, 0, 0, 0))
                bg.alpha_composite(img, (0, 0))
                bg.save(f"data/imgwelcome/{ctx.message.guild.id}.png")
                await ctx.send("Set image!")
            except Exception as e:
                await ctx.send(f"Failed to set image... {e}")
        else:
            if os.path.exists(f"data/imgwelcome/{ctx.message.guild.id}.png"):
                os.remove(f"data/imgwelcome/{ctx.message.guild.id}.png")
            await ctx.send("Reset Image.")

    def forbiddencheck(self, text:str):
        characters = string.ascii_letters + string.digits + " " + "'" + "!" + "." + "<" + ">" + "@" + "#" + ":"
        forbidden_char = 0
        for letter in text:
            if letter not in characters:
                forbidden_char += 1
        return forbidden_char

    @imgwelcome.command(name="text")
    async def img_text(self, ctx, *, text:str):
        """Set the image text, typing user will give the user as server will give the server name,

        Welcome user to server!"""
        if self.forbiddencheck(text) >= 1:
            return await ctx.send("Forbidden characters...")
        newtext = text.replace("user", "{0}").replace("server", "{1}")
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(f"UPDATE newimgwelcome SET content = \"{newtext}\" WHERE server = {ctx.message.guild.id}")
        await ctx.send("Updated!")

    @commands.command()
    @commands.is_owner()
    async def imggen(self, ctx, member:discord.Member=None):
        if member is None:
            member = ctx.message.author
        await self.on_member_join(member)

    async def _circle_border(self, circle_img_size: tuple):
        border_size = []
        for i in range(len(circle_img_size)):
            border_size.append(circle_img_size[0] + 8)
        return tuple(border_size)

    def _get_suffix(self, num):
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 10 <= num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = suffixes.get(num % 10, 'th')
        return suffix

    async def on_member_join(self, member):
        server = member.guild
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                if not await db.execute(f"SELECT 1 FROM newimgwelcome WHERE server = {server.id}"):
                    return
                else:
                    await db.execute(f"SELECT server, channel, content FROM newimgwelcome WHERE server = {server.id}")
                    alldata = await db.fetchall()
                    channel = alldata[0][1]
                    content = alldata[0][2]
        channel = self.bot.get_channel(int(channel))
        if not channel:
            return
        await channel.trigger_typing()

        if os.path.exists(f"data/imgwelcome/{server.id}.png"):
            background = Image.open(f"data/imgwelcome/{server.id}.png").convert("RGBA")
        else:
            background = Image.open("data/imgwelcome/transparent.png")

        async with aiohttp.ClientSession() as cs:
            async with cs.get(member.avatar_url_as(format="png")) as r:
                imgdata = await r.read()

        global welcome_picture
        welcome_picture = Image.new("RGBA", (500, 150))
        welcome_picture = ImageOps.fit(background, (500, 150), centering=(0.5, 0.5))
        welcome_picture.paste(background)
        welcome_picture = welcome_picture.resize((500, 150), Image.NEAREST)

        profile_area = Image.new("L", (512, 512), 0)
        draw = ImageDraw.Draw(profile_area)
        draw.ellipse(((0, 0), (512, 512)), fill=255)
        profile_area = profile_area.resize((128, 128), Image.ANTIALIAS)
        profile_picture = Image.open(BytesIO(imgdata))
        profile_area_output = ImageOps.fit(profile_picture, (128, 128), centering=(0, 0))
        profile_area_output.putalpha(profile_area)

        mask = Image.new('L', (512, 512), 0)
        draw_thumb = ImageDraw.Draw(mask)
        draw_thumb.ellipse((0, 0) + (512, 512), fill=255, outline=0)
        circle = Image.new("RGBA", (512, 512))
        draw_circle = ImageDraw.Draw(circle)
        draw_circle.ellipse([0, 0, 512, 512], fill=(255,255, 255, 180), outline=(255, 255, 255, 250))
        circle_border_size = await self._circle_border((128, 128))
        circle = circle.resize((circle_border_size), Image.ANTIALIAS)
        circle_mask = mask.resize((circle_border_size), Image.ANTIALIAS)
        circle_pos = (7 + int((136 - circle_border_size[0]) / 2))
        border_pos = (11 + int((136 - circle_border_size[0]) / 2))
        drawtwo = ImageDraw.Draw(welcome_picture)
        welcome_picture.paste(circle, (circle_pos, circle_pos), circle_mask)
        welcome_picture.paste(profile_area_output, (border_pos, border_pos), profile_area_output)

        uname = (str(member.name) + "#" + str(member.discriminator))

        def _outline(original_position: tuple, text: str, pixel_displacement: int, font, textoutline):
            op = original_position
            pd = pixel_displacement

            left = (op[0] - pd, op[1])
            right = (op[0] + pd, op[1])
            up = (op[0], op[1] - pd)
            down = (op[0], op[1] + pd)

            drawtwo.text(left, text, font=font, fill=(textoutline))
            drawtwo.text(right, text, font=font, fill=(textoutline))
            drawtwo.text(up, text, font=font, fill=(textoutline))
            drawtwo.text(down, text, font=font, fill=(textoutline))

            drawtwo.text(op, text, font=font, fill=(textoutline))

        welcome_font = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 50)

        _outline((150, 16), "Welcome", 1, welcome_font, (0, 0, 0, 255))
        drawtwo.text((150, 16), "Welcome", font=welcome_font, fill=(255, 255, 255, 230))
        name_font = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 30)
        name_font_medium = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 22)
        name_font_small = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 18)
        name_font_smallest = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 12)
        server_font = ImageFont.truetype("data/fonts/UniSansHeavy.otf", 20)

        if len(uname) <= 17:
            _outline((152, 63), uname, 1, name_font, (0, 0, 0, 255))
            drawtwo.text((152, 63), uname, font=name_font, fill=(255, 255, 255, 230))

        if len(uname) > 17:
            if len(uname) <= 23:
                _outline((152, 66), uname, 1, name_font_medium, (0, 0, 0, 255))
                drawtwo.text((152, 66), uname, font=name_font_medium, fill=(255, 255, 255, 230))

        if len(uname) >= 24:
            if len(uname) <= 32:
                _outline((152, 70), uname, 1, name_font_small, (0, 0, 0, 255))
                drawtwo.text((152, 70), uname, font=name_font_small, fill=(255, 255, 255, 230))

        if len(uname) >= 33:
            drawtwo.text((152, 73), uname, 1, name_font_smallest, (0, 0, 0, 255))
            drawtwo.text((152, 73), uname, font=name_font_smallest, fill=(255, 255, 255, 230))

        members = sorted(server.members, key=lambda m: m.joined_at).index(member) + 1

        member_number = str(members) + self._get_suffix(members)
        sname = str(member.guild.name) + '!' if len(str(member.guild.name)) <= 28 else str(member.guild.name)[
                                                                                         :23] + '...'

        _outline((152, 96), "You are the " + str(member_number) + " member", 1, server_font, (0, 0, 0, 255))
        drawtwo.text((152, 96), "You are the " + str(member_number) + " member", font=server_font, fill=(255, 255, 255, 230))
        _outline((152, 116), 'of ' + sname, 1, server_font, (0, 0, 0, 255))
        drawtwo.text((152, 116), 'of ' + sname, font=server_font, fill=(255, 255, 255, 230))

        welcome_picture.save("data/welcome.png")

        file = discord.File("data/welcome.png", filename="welcome.png")
        await channel.send(file=file, content=content.format(member.name, member.guild.name))

def setup(bot):
    bot.add_cog(IMGWelcome(bot))