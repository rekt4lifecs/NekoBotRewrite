from discord.ext import commands
import discord, aiohttp
import random, string, json, time
import pymysql

import config

class Donator:

    def __init__(self, bot):
        self.bot = bot
        self.donators = ["178189410871803904",
                             "205379510139486208",
                             "102165107244539904",
                             "270133511325876224",
                             "266277541646434305"]

    def id_generator(self, size=7, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @commands.command(name='trapcard')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def donator_trapcard(self, ctx, user: discord.Member):
        """Trap a user!"""

        author = ctx.message.author

        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()

        db.execute(f"SELECT userid FROM donator")
        alltokens = db.fetchall()
        tokenlist = []
        for x in range(len(alltokens)):
            tokenlist.append(int(alltokens[x][0]))

        if author.id not in tokenlist:
            return await ctx.send(embed=discord.Embed(color=0xff5630, title="Error",
                                                      description="You need to be a [donator](https://www.patreon.com/NekoBot) to use this command."))

        async with aiohttp.ClientSession() as session:
            url = f"http://37.59.36.62:10000/trapcard" \
                  f"?authorization={config.donator}" \
                  f"&name={user.name}" \
                  f"&author={author.name}" \
                  f"&image={user.avatar_url_as(format='png')}"
            async with session.get(url) as response:
                t = await response.json()
                await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=t['url']))

    @commands.command()
    @commands.is_owner()
    async def createkey(self, ctx):
        """Create a key"""
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        x1 = self.id_generator(size=4, chars=string.ascii_uppercase + string.digits)
        x2 = self.id_generator(size=4, chars=string.ascii_uppercase + string.digits)
        x3 = self.id_generator(size=4, chars=string.ascii_uppercase + string.digits)
        token = f"{x1}-{x2}-{x3}"
        await ctx.send(embed=discord.Embed(color=0xDEADBF, title="Token Generated", description=f"```css\n"
                                                                                                f"[ {token} ]```"))
        timenow = int(time.time())
        db.execute(f"INSERT INTO donator VALUES (0, \"{token}\", {timenow})")
        connection.commit()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def redeem(self, ctx, *, key: str):
        """Redeem your donation key"""
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        x = db.execute(f"SELECT 1 FROM donator WHERE token = \"{key}\"")
        if x == 0:
            return await ctx.send("**Invalid key**")
        db.execute(f"SELECT userid FROM donator WHERE token = \"{key}\"")
        user = int(db.fetchone()[0])
        if user == 0:
            db.execute(f"UPDATE donator SET userid = {ctx.message.author.id} WHERE token = \"{key}\"")
            connection.commit()
            channel = self.bot.get_channel(431887286246834178)
            await channel.send(embed=discord.Embed(color=0x8bff87,
                                                   title="Token Accepted",
                                                   description=f"```css\n"
                                                               f"User: {ctx.message.author.name} ({ctx.message.author.id})\n"
                                                               f"Key: [ {key} ]").set_thumbnail(url=ctx.message.author.avatar_url))
            return await ctx.send("**Token Accepted!**")
        else:
            return await ctx.send("**Token already in use.**")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donate(self, ctx):
        """Donate"""
        return await ctx.send(embed=discord.Embed(color=0xff5630, title="OwO Whats This",
                                                  description="Come donate on [Patreon](https://www.patreon.com/NekoBot) to get access to special features OwO"))

    @commands.command(name='upload')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def owner_upload(self, ctx):
        """File Uploader"""
        author = ctx.message.author
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()

        db.execute(f"SELECT userid FROM donator")
        alltokens = db.fetchall()
        tokenlist = []
        for x in range(len(alltokens)):
            tokenlist.append(int(alltokens[x][0]))

        if author.id not in tokenlist:
            return await ctx.send(embed=discord.Embed(color=0xff5630, title="Error",
                                                      description="You need to be a [donator](https://www.patreon.com/NekoBot) to use this command."))

        await ctx.send("**Send an image/file to upload. Type `cancel` to cancel.**")

        def check(m):
            return m.author == author and m.channel == ctx.message.channel

        msg = await self.bot.wait_for('message', check=check)

        if msg.content in ['cancel', 'Cancel']:
            return await ctx.send("**Cancelled.**")

        try:
            randomnum = self.id_generator()
            url = msg.attachments[0].url
            attachment = str(url).rpartition('.')[2]
            if attachment not in ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp']:
                return await ctx.send("**File type is forbiddon.**")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    t = await response.read()
                    with open(f"/home/www/{randomnum}.{attachment}", "wb") as f:
                        f.write(t)
            await ctx.send(f"https://nekobot.xyz/{randomnum}.{attachment}")
        except Exception as e:
            return await ctx.send(f"**Error uploading file**\n\n{e}")

def setup(bot):
    bot.add_cog(Donator(bot))