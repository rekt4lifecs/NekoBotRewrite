from discord.ext import commands
import discord, asyncio, aiomysql, config

class Marriage:

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

        if user == author:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="You can't marry yourself."))
            return
        if await self.userexists('marriage', author):
            await ctx.send(embed=discord.Embed(color=0xff5630, description="You are already married"))
            return
        elif await self.userexists('marriage', user):
            await ctx.send(embed=discord.Embed(color=0xff5630, description="That user is already married."))
            return
        else:
            await ctx.send(f"{author.name} is wanting to marry {user.name}!\n"
                           f"{user.mention} type yes to accept!")

            def check(m):
                return m.content == 'yes' and m.channel == ctx.message.channel and m.author == user

            try:
                await self.bot.wait_for('message', check=check, timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(color=0xff5630, description="Marriage Cancelled."))
                return

            await ctx.send(f"🎉 {author.mention} ❤ {user.mention} 🎉")
            await self.execute(f"INSERT INTO marriage VALUES({author.id}, {user.id})", commit=True)
            await self.execute(f"INSERT INTO marriage VALUES({user.id}, {author.id})", commit=True)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def divorce(self, ctx, user : discord.Member):
        """Divorce ;-;"""
        author = ctx.message.author

        if user == author:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="How can you divorce yourself?"))
            return

        if await self.userexists('marriage', author) is False:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="You are not married"))
            return
        elif await self.userexists('marriage', user) is False:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="That user isn't married"))
            return
        x = await self.execute(f"SELECT marryid FROM marriage WHERE userid = {author.id}", isSelect=True)
        user_married_to = int(x[0])
        if user_married_to != user.id:
            await ctx.send(embed=discord.Embed(color=0xff5630, description="You are not married to that user"))
            return
        else:
            await ctx.send(f"{author.name} divorced {user.name} 😦😢")
            await self.execute(f"DELETE FROM marriage WHERE userid = {author.id}", commit=True)
            await self.execute(f"DELETE FROM marriage WHERE userid = {user.id}", commit=True)

def setup(bot):
    bot.add_cog(Marriage(bot))