from discord.ext import commands
import discord, asyncio
import ujson
import rethinkdb as r
from .utils import chat_formatting

# Languages
languages = ["english", "weeb", "tsundere", "polish", "spanish", "french"]
lang = {}

for l in languages:
    with open("lang/%s.json" % l, encoding="utf-8") as f:
        lang[l] = ujson.load(f)

def getlang(la:str):
    return lang.get(la, None)

class Marriage:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def marry(self, ctx, user : discord.Member):
        """Marry someone OwO"""
        author = ctx.author

        lang = await self.bot.redis.get(f"{ctx.author.id}-lang")
        if lang:
            lang = lang.decode("utf8")
        else:
            lang = "english"

        if user == author:
            return await ctx.send(chat_formatting.bold(getlang(lang)["marriage"]["marry_self"]))
        if await r.table("marriage").get(str(author.id)).run(self.bot.r_conn):
            return await ctx.send(chat_formatting.bold(getlang(lang)["marriage"]["author_married"]))
        elif await r.table("marriage").get(str(user.id)).run(self.bot.r_conn):
            return await ctx.send(chat_formatting.bold(getlang(lang)["marriage"]["user_married"]))
        else:
            await ctx.send(getlang(lang)["marriage"]["marry_msg"].format(author, user))

            def check(m):
                return m.channel == ctx.message.channel and m.author == user

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=15.0)
                if msg.content.lower() != "yes":
                    return await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["cancelled"]))
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["cancelled"]))
                return

            await ctx.send(f"🎉 {author.mention} ❤ {user.mention} 🎉")
            await r.table("marriage").insert({"id": str(author.id), "marriedTo": str(user.id)}).run(self.bot.r_conn)
            await r.table("marriage").insert({"id": str(user.id), "marriedTo": str(author.id)}).run(self.bot.r_conn)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def divorce(self, ctx):
        """Divorce ;-;"""
        author = ctx.message.author

        lang = await self.bot.redis.get(f"{ctx.author.id}-lang")
        if lang:
            lang = lang.decode("utf8")
        else:
            lang = "english"

        if not await r.table("marriage").get(str(author.id)).run(self.bot.r_conn):
            return await ctx.send(chat_formatting.bold(getlang(lang)["marriage"]["not_married"]))
        x = await r.table("marriage").get(str(author.id)).run(self.bot.r_conn)
        user_married_to = int(x["marriedTo"])
        married_to_name = await self.bot.get_user_info(user_married_to)

        def check(m):
            return m.channel == ctx.message.channel and m.author == author

        await ctx.send("**Are you sure you want to divorce %s?**" % (married_to_name,))

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=15.0)
            if msg.content.lower() != "yes":
                return await ctx.send("**Cancelled.**")
        except asyncio.TimeoutError:
            await ctx.send("**Cancelled.**")
            return

        await ctx.send(f"{author.name} divorced {married_to_name} 😦😢")
        await r.table("marriage").get(str(author.id)).delete().run(self.bot.r_conn)
        await r.table("marriage").get(str(user_married_to)).delete().run(self.bot.r_conn)

def setup(bot):
    bot.add_cog(Marriage(bot))