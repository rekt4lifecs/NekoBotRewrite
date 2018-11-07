from discord.ext import commands
import discord, asyncio
import gettext
import rethinkdb as r
from .utils.chat_formatting import bold

class Marriage:

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
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
    @commands.guild_only()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def marry(self, ctx, user : discord.Member):
        """Marry someone OwO"""
        _ = await self._get_text(ctx)
        if user == ctx.author:
            return await ctx.send(bold(_("You can't marry yourself.")))
        author_data = await r.table("marriage").get(str(ctx.author.id)).run(self.bot.r_conn)
        if not author_data:
            author_data = {
                "id": str(ctx.author.id),
                "marriedTo": []
            }
            await r.table("marriage").insert(author_data).run(self.bot.r_conn)

        if str(user.id) in author_data.get("marriedTo", []):
            return await ctx.send(bold(_("You are already married to that user.")))
        elif len(author_data.get("marriedTo", [])) >= 5:
            return await ctx.send(bold(_("You are married to too many users")))

        a_name = ctx.author.name.replace("@", "@\u200B")
        u_name = user.name.replace("@", "@\u200B")
        await ctx.send(_("%s is wanting to marry %s!\n%s type yes to accept!") % (a_name, u_name, user.mention))

        try:
            msg = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.message.channel and x.author == user, timeout=15.0)
            if msg.content.lower() != "yes":
                return await ctx.send(_("Marriage Cancelled."))
        except asyncio.TimeoutError:
            return await ctx.send(_("Marriage Cancelled."))

        await ctx.send(f"🎉 {ctx.author.mention} ❤ {user.mention} 🎉")

        user_data = await r.table("marriage").get(str(user.id)).run(self.bot.r_conn)
        if not user_data:
            user_data = {
                "id": str(user.id),
                "marriedTo": []
            }
            await r.table("marriage").insert(user_data).run(self.bot.r_conn)

        author_marriedTo = author_data.get("marriedTo", [])
        user_marriedTo = user_data.get("marriedTo", [])
        author_marriedTo.append(str(user.id))
        user_marriedTo.append(str(ctx.author.id))
        await r.table("marriage").get(str(ctx.author.id)).update({"marriedTo": author_marriedTo}).run(self.bot.r_conn)
        await r.table("marriage").get(str(user.id)).update({"marriedTo": user_marriedTo}).run(self.bot.r_conn)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def divorce(self, ctx, user: discord.Member):
        """Divorce ;-;"""
        _ = await self._get_text(ctx)

        if user == ctx.author:
            return await ctx.send("You can't divorce yourself")
        author_data = await r.table("marriage").get(str(ctx.author.id)).run(self.bot.r_conn)
        if not author_data:
            return await ctx.send(bold(_("You are not married")))
        user_data = await r.table("marriage").get(str(user.id)).run(self.bot.r_conn)
        if not user_data:
            return await ctx.send(_("That user is not married to anyone"))
        if not str(ctx.author.id) in user_data.get("marriedTo", []):
            return await ctx.send(_("That user is not married to you"))

        await ctx.send(_("**Are you sure you want to divorce %s?**") % user.name.replace("@", "@\u200B"))

        try:
            msg = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.message.channel and x.author == ctx.author, timeout=15.0)
            if msg.content.lower() != "yes":
                return await ctx.send(_("**Cancelled.**"))
        except asyncio.TimeoutError:
            return await ctx.send(_("**Cancelled.**"))

        new_author_married = []
        for u in author_data.get("marriedTo", []):
            if u != str(user.id):
                new_author_married.append(u)

        new_user_married = []
        for u in user_data.get("marriedTo", []):
            if u != str(ctx.author.id):
                new_user_married.append(u)

        await r.table("marriage").get(str(user.id)).update({"marriedTo": new_user_married}).run(self.bot.r_conn)
        await r.table("marriage").get(str(ctx.author.id)).update({"marriedTo": new_author_married}).run(self.bot.r_conn)
        await ctx.send("%s divorced %s 😦😢" % (ctx.author.name.replace("@", "@\u200B"), user.name.replace("@", "@\u200B")))

def setup(bot):
    bot.add_cog(Marriage(bot))