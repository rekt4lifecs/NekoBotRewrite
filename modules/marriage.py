from discord.ext import commands
import discord, asyncio
import gettext
import rethinkdb as r
from .utils import chat_formatting

class Marriage:

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb"]
        for x in self.languages:
            self.lang[x] = gettext.translation("marriage", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def marry(self, ctx, user : discord.Member):
        """Marry someone OwO"""
        author = ctx.author

        _ = await self._get_text(ctx)

        if user == author:
            return await ctx.send(chat_formatting.bold(_("You can't marry yourself.")))
        if await r.table("marriage").get(str(author.id)).run(self.bot.r_conn):
            return await ctx.send(chat_formatting.bold(_("You are already married")))
        elif await r.table("marriage").get(str(user.id)).run(self.bot.r_conn):
            return await ctx.send(chat_formatting.bold(_("That user is already married")))
        else:
            a_name = author.name.replace("@", "@\u200B")
            u_name = user.name.replace("@", "@\u200B")
            await ctx.send(_("%s is wanting to marry %s!\n%s type yes to accept!") % (a_name, u_name, user.mention))

            def check(m):
                return m.channel == ctx.message.channel and m.author == user

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=15.0)
                if msg.content.lower() != "yes":
                    return await ctx.send(embed=discord.Embed(color=0xff5630, description=_("Marriage Cancelled.")))
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(color=0xff5630, description=_("Marriage Cancelled.")))
                return

            await ctx.send(f"🎉 {author.mention} ❤ {user.mention} 🎉")
            await r.table("marriage").insert({"id": str(author.id), "marriedTo": str(user.id)}).run(self.bot.r_conn)
            await r.table("marriage").insert({"id": str(user.id), "marriedTo": str(author.id)}).run(self.bot.r_conn)

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def divorce(self, ctx):
        """Divorce ;-;"""
        author = ctx.author

        _ = await self._get_text(ctx)

        if not await r.table("marriage").get(str(author.id)).run(self.bot.r_conn):
            return await ctx.send(chat_formatting.bold(_("You are not married")))
        x = await r.table("marriage").get(str(author.id)).run(self.bot.r_conn)
        user_married_to = int(x["marriedTo"])
        married_to_name = (await self.bot.get_user_info(user_married_to)).replace("@", "@\u200B")

        def check(m):
            return m.channel == ctx.message.channel and m.author == author

        await ctx.send(_("**Are you sure you want to divorce %s?**") % (married_to_name,))

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=15.0)
            if msg.content.lower() != "yes":
                return await ctx.send(_("**Cancelled.**"))
        except asyncio.TimeoutError:
            await ctx.send(_("**Cancelled.**"))
            return

        await ctx.send(_("%s divorced %s 😦😢") % (author.name.replace("@", "@\u200B"), married_to_name))
        await r.table("marriage").get(str(author.id)).delete().run(self.bot.r_conn)
        await r.table("marriage").get(str(user_married_to)).delete().run(self.bot.r_conn)

def setup(bot):
    bot.add_cog(Marriage(bot))