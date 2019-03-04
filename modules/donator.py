from discord.ext import commands
import discord
import rethinkdb as r
import aiohttp
from prettytable import PrettyTable

import random
import string
import time
import logging

from config import webhook_id, webhook_token
from .utils.hastebin import post as haste
import gettext

log = logging.getLogger()

class Donator:

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("donator", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

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
        _ = await self._get_text(ctx)

        if not await self.__has_donated(ctx.author.id):
            return await ctx.send(_("You need to be a **donator** to use this command."))

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
        _ = await self._get_text(ctx)

        if not await self.__has_donated(ctx.author.id):
            await ctx.send(_("You can donate at <https://www.patreon.com/NekoBot>!"))
        else:
            await ctx.send(_("You have already donated <:ChocoHappy:429538812855582721><a:rainbowNekoDance:462373594555613214>"))

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
        _ = await self._get_text(ctx)

        if await r.table("autolooder").get(str(ctx.guild.id)).run(self.bot.r_conn):
            await r.table("autolooder").get(str(ctx.guild.id)).delete().run(self.bot.r_conn)
            return await ctx.send(_("I have disable the autolooder for you <:lurk:356825018702888961>"))

        if not await self.__has_donated(ctx.author.id):
            return await ctx.send(_("You have not donated :c, you can donate at <https://www.patreon.com/NekoBot> <:AwooHappy:471598416238215179>"))

        if not channel:
            return await self.bot.send_cmd_help(ctx)

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
        await ctx.send(_("Enabled autolooder for `%s`!") % channel.name)


    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(aliases=["autoloodersetting", "autolewdsetting", "autoloodsettings", "autolewdsettings", "autoloodersettings"])
    async def autoloodsetting(self, ctx, imgtype: str = None):
        """Toggle autolood options for the current servers autolewder

        Image Types: pgif, 4k, hentai, holo, lewdneko, neko, lewdkitsune, kemonomimi, anal, hentai_anal, gonewild, kanna, ass, pussy, thigh
        Example: n!autoloodtoggle holo"""
        _ = await self._get_text(ctx)

        data = await r.table("autolooder").get(str(ctx.guild.id)).run(self.bot.r_conn)
        if not data:
            return await ctx.send("Autolooder is not enabled on this server")

        if imgtype is None:
            return await ctx.send("Enabled Types: %s" % ", ".join(["`%s`" % i for i in data.get("choices", [])]))

        options = ["pgif", "4k", "hentai", "holo", "lewdneko", "neko", "lewdkitsune", "kemonomimi", "anal",
                   "hentai_anal", "gonewild", "kanna", "ass", "pussy", "thigh"]

        imgtype = imgtype.lower()
        if imgtype not in options:
            return await ctx.send("Not a valid type, valid types: %s" % ", ".join(["`%s`" % i for i in options]))

        if imgtype in data.get("choices", []):
            newchoices = []
            for choice in data.get("choices", []):
                if choice != imgtype:
                    newchoices.append(choice)
        else:
            newchoices = data.get("choices", []) + [imgtype]

        await r.table("autolooder").get(str(ctx.guild.id)).update({"choices": newchoices}).run(self.bot.r_conn)
        await ctx.send("Toggled option for %s!" % imgtype)


def setup(bot):
    bot.add_cog(Donator(bot))