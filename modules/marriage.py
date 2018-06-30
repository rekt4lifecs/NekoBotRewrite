from discord.ext import commands
import discord, asyncio
import ujson

# Languages
languages = ["english", "weeb", "tsundere", "polish", "spanish"]
lang = {}

for l in languages:
    with open("lang/%s.json" % l, encoding="utf-8") as f:
        lang[l] = ujson.load(f)

def getlang(la:str):
    return lang.get(la, None)

class Marriage:

    def __init__(self, bot):
        self.bot = bot

    async def execute(self, query: str, isSelect: bool = False, fetchAll: bool = False, commit: bool = False):
        async with self.bot.sql_conn.acquire() as conn:
            async with conn.cursor() as db:
                await db.execute(query)
                if isSelect:
                    if fetchAll:
                        values = await db.fetchall()
                    else:
                        values = await db.fetchone()
                if commit:
                    await conn.commit()
            if isSelect:
                return values

    async def userexists(self, datab : str, user : discord.Member):
        user = user.id
        x = await self.execute(f"SELECT 1 FROM {datab} WHERE userid = {user}", isSelect=True)
        if not x:
            return False
        else:
            return True

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def marry(self, ctx, user : discord.Member):
        """Marry someone OwO"""
        author = ctx.message.author

        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if user == author:
            await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["marry_self"]))
            return
        if await self.userexists('marriage', author):
            await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["author_married"]))
            return
        elif await self.userexists('marriage', user):
            await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["user_married"]))
            return
        else:
            await ctx.send(getlang(lang)["marriage"]["marry_msg"].format(author, user))

            def check(m):
                return m.channel == ctx.message.channel and m.author == user

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                if msg.content.lower() != "yes":
                    return await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["cancelled"]))
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["cancelled"]))
                return

            await ctx.send(f"🎉 {author.mention} ❤ {user.mention} 🎉")
            await self.execute(f"INSERT INTO marriage VALUES({author.id}, {user.id})", commit=True)
            await self.execute(f"INSERT INTO marriage VALUES({user.id}, {author.id})", commit=True)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def divorce(self, ctx):
        """Divorce ;-;"""
        author = ctx.message.author

        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if await self.userexists('marriage', author) is False:
            await ctx.send(embed=discord.Embed(color=0xff5630, description=getlang(lang)["marriage"]["not_married"]))
            return
        x = await self.execute(f"SELECT marryid FROM marriage WHERE userid = {author.id}", isSelect=True)
        user_married_to = int(x[0])
        married_to_name = self.bot.get_user(user_married_to)
        if married_to_name:
            married_to_name = married_to_name.name
        else:
            married_to_name = "Unknown user"

        def check(m):
            return m.channel == ctx.message.channel and m.author == author

        await ctx.send("Are you sure you want to divorce %s?" % (married_to_name,))

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            if msg.content.lower() != "yes":
                return await ctx.send(
                    embed=discord.Embed(color=0xff5630, description="Cancelled"))
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="Cancelled"))
            return

        await ctx.send(f"{author.name} divorced {married_to_name} 😦😢")
        await self.execute(f"DELETE FROM marriage WHERE userid = {author.id}", commit=True)
        await self.execute(f"DELETE FROM marriage WHERE userid = {user_married_to}", commit=True)

def setup(bot):
    bot.add_cog(Marriage(bot))