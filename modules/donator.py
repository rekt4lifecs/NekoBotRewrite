from discord.ext import commands
import discord
import rethinkdb as r
import aiohttp
import logging

log = logging.getLogger()

class Donator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def __has_donated(self, user:int):
        data = await self.bot.redis.get("donate:{}".format(user))
        if data:
            return True
        else:
            return False

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setdonate(self, ctx, UserID:int, level: int):
        """Send a user their donation key."""
        if level == -1:
            await self.bot.redis.delete("donate:{}".format(UserID))
        else:
            await self.bot.redis.set("donate:{}".format(UserID), level)
        await ctx.message.add_reaction("👌")

    @commands.command(name='trapcard')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donator_trapcard(self, ctx, user: discord.Member):
        """Trap a user!"""
        await ctx.trigger_typing()

        if not await self.__has_donated(ctx.author.id):
            return await ctx.send("You need to be a **donator** to use this command.")

        async with aiohttp.ClientSession() as session:
            url = f"https://nekobot.xyz/api/imagegen" \
                  f"?type=trap" \
                  f"&name={user.name}" \
                  f"&author={ctx.author.name}" \
                  f"&image={user.avatar_url_as(format='png')}"
            async with session.get(url) as response:
                t = await response.json()
                await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=t["message"]))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donate(self, ctx):
        await ctx.trigger_typing()

        if not await self.__has_donated(ctx.author.id):
            await ctx.send("You can donate at <https://www.patreon.com/NekoBot>!")
        else:
            await ctx.send("You have already donated <:ChocoHappy:429538812855582721><a:rainbowNekoDance:462373594555613214>")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=["autolood", "autolewd"])
    async def autolooder(self, ctx, channel:discord.TextChannel=None):
        """
        Enable/Disable the autolooder for your server, mention an already added channel to disable.
        Example:
            n!autolooder #autolood_channel
            or
            n!autolooder autolood_channel"""

        if await r.table("autolooder").get(str(ctx.guild.id)).run(self.bot.r_conn):
            await r.table("autolooder").get(str(ctx.guild.id)).delete().run(self.bot.r_conn)
            return await ctx.send("I have disable the autolooder for you <:lurk:356825018702888961>")

        if not await self.__has_donated(ctx.author.id):
            return await ctx.send("You have not donated :c, you can donate at <https://www.patreon.com/NekoBot> <:AwooHappy:471598416238215179>")

        if not channel:
            return await ctx.send_help(ctx.command)

        data = {
            "id": str(ctx.guild.id),
            "channel": str(channel.id),
            "user": str(ctx.author.id),
            "choices": [
                "hentai",
                "neko",
                "hentai_anal",
                "lewdneko",
                "lewdkitsune"
            ]
        }
        await r.table("autolooder").insert(data).run(self.bot.r_conn)
        await ctx.send("Enabled autolooder for `{}`!".format(channel.name))


    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(aliases=["autoloodersetting", "autolewdsetting", "autoloodsettings", "autolewdsettings", "autoloodersettings"])
    async def autoloodsetting(self, ctx, imgtype: str = None):
        """Toggle autolood options for the current servers autolewder

        Image Types: pgif, 4k, hentai, holo, lewdneko, neko, lewdkitsune, kemonomimi, anal, hentai_anal, gonewild, kanna, ass, pussy, thigh
        Example: n!autoloodtoggle holo"""

        data = await r.table("autolooder").get(str(ctx.guild.id)).run(self.bot.r_conn)
        if not data:
            return await ctx.send("Autolooder is not enabled on this server")

        if imgtype is None:
            return await ctx.send("Enabled Types: {}".format(", ".join(["`{}`".format(i) for i in data.get("choices", [])])))

        options = ["pgif", "4k", "hentai", "holo", "lewdneko", "neko", "lewdkitsune", "kemonomimi", "anal",
                   "hentai_anal", "gonewild", "kanna", "ass", "pussy", "thigh"]

        imgtype = imgtype.lower()
        if imgtype not in options:
            return await ctx.send("Not a valid type, valid types: {}".format(", ".join(["`{}`".format(i) for i in options])))

        if imgtype in data.get("choices", []):
            newchoices = []
            for choice in data.get("choices", []):
                if choice != imgtype:
                    newchoices.append(choice)
        else:
            newchoices = data.get("choices", []) + [imgtype]

        await r.table("autolooder").get(str(ctx.guild.id)).update({"choices": newchoices}).run(self.bot.r_conn)
        await ctx.send("Toggled option for {}!".format(imgtype))

    @commands.group()
    @commands.guild_only()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def twitter(self, ctx):

        has_donated = 0
        d = await self.bot.redis.get("donate:{}".format(ctx.author.id))
        if d:
            has_donated = int(d)

        if has_donated <= 0:
            return await ctx.send("You have not donated")

        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @twitter.command(name="set")
    async def twitter_set(self, ctx, channel: discord.TextChannel):
        """Set twitter feed to a channel"""
        if not channel.is_nsfw():
            return await ctx.send("The channel must be an NSFW channel.")
        data = await r.table("twitter2").get(str(ctx.guild.id)).run(self.bot.r_conn)
        if data:
            await r.table("twitter2").get(str(ctx.guild.id)).update({
                "channel": str(channel.id)
            }).run(self.bot.r_conn)
            return await ctx.send("Updated channel to {}".format(channel.mention))
        await r.table("twitter2").insert({
            "id": str(ctx.guild.id),
            "channel": str(channel.id),
            "accounts": [],
            "user": str(ctx.author.id)
        }).run(self.bot.r_conn)
        await ctx.send("Set channel to {}, you can add users with `n!tweet add <username>`".format(channel.mention))

    @twitter.command(name="add")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def twitter_add(self, ctx, username: str):
        """Add a user to your feed"""
        guild = await r.table("twitter2").get(str(ctx.guild.id)).run(self.bot.r_conn)
        if not guild:
            return await ctx.send("Twitter hasn't been setup for this server, use `n!twitter set <channel>` to set it up.")
        d = int((await self.bot.redis.get("donate:{}".format(ctx.author.id))))
        accounts = 0
        if d == 1:
            accounts = 5
        elif d == 2:
            accounts = 10
        if accounts <= len(guild["accounts"]):
            return await ctx.send("You already have set the most you can for this server. You can remove accounts using `n!twitter remove <username>`")
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://localhost:8090/gettwitteruser?username={}".format(username.replace("@", ""))) as res:
                res = await res.json()
        if not res["results"]:
            return await ctx.send("No results found for this user.")
        result = str(res["results"][0])
        if result in guild["accounts"]:
            return await ctx.send("This account is already set to your feeds")
        guild["accounts"].append(result)
        await r.table("twitter2").get(str(ctx.guild.id)).update({"accounts": guild["accounts"]}).run(self.bot.r_conn)
        await ctx.send("That user has been added to your feed")

    @twitter.command(name="remove")
    async def twitter_remove(self, ctx, username: str):
        """Remove a user to your feed"""
        guild = await r.table("twitter2").get(str(ctx.guild.id)).run(self.bot.r_conn)
        if not guild:
            return await ctx.send("Twitter hasn't been setup for this server, use `n!twitter set <channel>` to set it up.")
        username = username.replace("@", "")
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://localhost:8090/gettwitteruser?username={}".format(username.replace("@", ""))) as res:
                res = await res.json()
        if not res["results"]:
            return await ctx.send("No results found for this user.")
        result = str(res["results"][0])
        if result not in guild["accounts"]:
            return await ctx.send("This user has not been added yet")
        l = list()
        for account in guild["accounts"]:
            if account != result:
                l.append(account)
        await r.table("twitter2").get(str(ctx.guild.id)).update({"accounts": l}).run(self.bot.r_conn)
        await ctx.send("Removed user")

    @twitter.command(name="clear")
    async def twitter_clear(self, ctx):
        """Remove twitter feeds from your server"""
        guild = await r.table("twitter2").get(str(ctx.guild.id)).run(self.bot.r_conn)
        if not guild:
            return await ctx.send("Twitter hasn't been setup for this server.")
        await r.table("twitter2").get(str(ctx.guild.id)).delete().run(self.bot.r_conn)
        await ctx.send("Removed Twitter feeds from this server.")

def setup(bot):
    bot.add_cog(Donator(bot))
