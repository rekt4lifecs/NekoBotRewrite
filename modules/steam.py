from discord.ext import commands
import config, discord, aiohttp

class Steam:
    """Get Steam Stats"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def steam(self, ctx, appid : int):
        """Get Steam stats with an APPID"""
        try:
            async with aiohttp.ClientSession() as cs:
                url = f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={config.steam.token}&appid={appid}"
                async with cs.get(url) as r:
                    res = await r.json()
        except:
            await ctx.send("Couldn't contact steam.")
        game = res['game']
        if res == {}:
            await ctx.send("Steam game could not be found.")
        else:
            em = discord.Embed(title=game['gameName'],
                                color=0xDEADBF)
            em.add_field(name="Version", value=game['gameVersion'])

            try:
                gameA = game['availableGameStats']['achievements']
                gameB = [x['displayName'] for x in gameA]
                if len(gameB) < 512:
                    em.add_field(name="Achievements", value=str(gameB).replace("[", "").replace("]", "").replace("'", ""))
                else:
                    pass
            except:
                pass

            await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Steam(bot))