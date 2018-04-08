from discord.ext import commands
import discord, aiohttp
import random, string, time
import datetime
import aiomysql
import config

class Donator:

    def __init__(self, bot):
        self.bot = bot

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
        connection.close()
        if isSelect:
            return values

    def id_generator(self, size=7, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @commands.command(name='trapcard')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def donator_trapcard(self, ctx, user: discord.Member):
        """Trap a user!"""

        author = ctx.message.author

        alltokens = await self.execute(isSelect=True, fetchAll=True, query="SELECT userid FROM donator")
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
        x1 = self.id_generator(size=4, chars=string.ascii_uppercase + string.digits)
        x2 = self.id_generator(size=4, chars=string.ascii_uppercase + string.digits)
        x3 = self.id_generator(size=4, chars=string.ascii_uppercase + string.digits)
        token = f"{x1}-{x2}-{x3}"
        await ctx.send(embed=discord.Embed(color=0xDEADBF, title="Token Generated", description=f"```css\n"
                                                                                                f"[ {token} ]```"))
        timenow = int(time.time())
        await self.execute(query=f"INSERT INTO donator VALUES (0, \"{token}\", {timenow})", commit=True)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def redeem(self, ctx, *, key: str):
        """Redeem your donation key"""
        x = await self.execute(query=f"SELECT 1 FROM donator WHERE token = \"{key}\"", isSelect=True)
        if not x:
            return await ctx.send("**Invalid key**")
        alltokens = await self.execute(query="SELECT userid FROM donator", isSelect=True, fetchAll=True)
        tokenlist = []
        for x in range(len(alltokens)):
            tokenlist.append(int(alltokens[x][0]))
        if ctx.message.author.id in tokenlist:
            return await ctx.send("**You already have a token activated!**")
        user = await self.execute(query=f"SELECT userid FROM donator WHERE token = \"{key}\"",
                                      isSelect=True)
        if int(user[0]) == 0:
            await self.execute(query=f"UPDATE donator SET userid = {ctx.message.author.id} WHERE token = \"{key}\"",
                                   commit=True)
            channel = self.bot.get_channel(431887286246834178)
            await channel.send(embed=discord.Embed(color=0x8bff87,
                                                   title="Token Accepted",
                                                   description=f"```css\n"
                                                               f"User: {ctx.message.author.name} ({ctx.message.author.id})\n"
                                                               f"Key: [ {key} ]```").set_thumbnail(url=ctx.message.author.avatar_url))
            return await ctx.send("**Token Accepted!**")
        else:
            channel = self.bot.get_channel(431887286246834178)
            await channel.send(embed=discord.Embed(color=0xff6f3f,
                                                   title="Token Denied",
                                                   description=f"```css\n"
                                                               f"User: {ctx.message.author.name} ({ctx.message.author.id})\n"
                                                               f"Key: [ {key} ]```").set_thumbnail(url=ctx.message.author.avatar_url))
            return await ctx.send("**Token already in use.**")

    @commands.command()
    @commands.is_owner()
    async def delkey(self, ctx, *, key:str):
        """Delete a key"""
        x = await self.execute(query=f"SELECT 1 FROM donator WHERE token = \"{key}\"", isSelect=True)
        if not x:
            return await ctx.send("**Invalid key**")
        else:
            await self.execute(query=f"DELETE FROM donator WHERE token = \"{key}\"", commit=True)
            await ctx.send(f"**Key `{key}` has been deleted.**")
            embed = discord.Embed(color=0xff6f3f, title="Token Deleted",
                                  description=f"```css\n"
                                              f"Key: [ {key} ] \n"
                                              f"```")
            channel = self.bot.get_channel(431887286246834178)
            return await channel.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donate(self, ctx):
        """Donate or Show key time left."""
        alltokens = await self.execute(query="SELECT userid FROM donator", isSelect=True, fetchAll=True)
        tokenlist = []
        for x in range(len(alltokens)):
            tokenlist.append(int(alltokens[x][0]))
        if ctx.message.author.id in tokenlist:
            user_token = await self.execute(query=f"SELECT token, usetime FROM donator WHERE userid = {ctx.message.author.id}",
                                                isSelect=True)
            timeconvert = datetime.datetime.fromtimestamp(int(user_token[1])).strftime('%Y-%m-%d')
            embed = discord.Embed(color=0xDEADBF, title="Key Info", description=f"Key: `XXXX-XXXX-{user_token[0][-4:]}`\n"
                                                                                f"Expiry Date: `{timeconvert}`")
            return await ctx.send(embed=embed)
        else:
            return await ctx.send(embed=discord.Embed(color=0xff5630, title="OwO Whats This",
                                                  description="Come donate on [Patreon](https://www.patreon.com/NekoBot) to get access to special features OwO"))

    @commands.command(name='upload')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def donator_upload(self, ctx):
        """File Uploader"""
        author = ctx.message.author

        alltokens = await self.execute(query="SELECT userid FROM donator", isSelect=True, fetchAll=True)
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