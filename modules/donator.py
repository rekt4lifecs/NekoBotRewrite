from discord.ext import commands
import discord, aiohttp
import random, string, json

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

        if author.id not in self.donators:
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

        if author.id not in self.donators:
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