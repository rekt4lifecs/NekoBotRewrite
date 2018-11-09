from discord.ext import commands
import discord, config, aiohttp
import base64, json
import os
import gettext

class Games:

    def __init__(self, bot):
        self.bot = bot
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("games", localedir="locale", languages=[x])

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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def osu(self, ctx, username:str):
        """Get osu stats"""
        _ = await self._get_text(ctx)
        try:
            await ctx.trigger_typing()
            url = "https://osu.ppy.sh/api/get_user?k=%s&u=%s" % (config.osu_key, username,)
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    data = await r.json()
            if data == []:
                return await ctx.send(_("User not found."))

            data = data[0]
            level = float(data["level"])
            rank = data["pp_rank"]
            crank = data["pp_country_rank"]
            accuracy = int(float(data["accuracy"]))
            pp = int(float(data["pp_raw"]))

            ss = int(data["count_rank_ss"])
            ssp = int(data["count_rank_ssh"])
            s = int(data["count_rank_s"])
            sp = int(data["count_rank_sh"])
            a = int(data["count_rank_a"])

            int_level = int(level)
            next_level = int_level + 1

            score = int((1 - (next_level - level)) * 100)
            filled_progbar = round(score / 100 * 10)
            level_graphx = '█' * filled_progbar + '‍ ‍' * (10 - filled_progbar)

            msg = _("OSU! Profile for `%s`\n") % username
            msg += "```\n"
            msg += _("Level - %s [ %s ] %s\n") % (int_level, level_graphx, next_level,)
            msg += _("Rank - %s\n") % rank
            msg += _("Country Rank - %s\n") % crank
            msg += _("Accuracy - %s\n") % str(accuracy) + "%"
            msg += _("PP - %s\n") % pp
            msg += _("SS - %s (SS+ %s)\n") % (ss, ssp,)
            msg += _("S  - %s (S+ %s)\n") % (s, sp,)
            msg += _("A  - %s\n") % a
            msg += "```"

            await ctx.send(msg)

        except Exception as e:
            return await ctx.send(_("Failed to fetch data, %s") % e)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def minecraft(self, ctx, username:str):
        _ = await self._get_text(ctx)
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as r:
                    res = await r.json()
            user_id = res['id']
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{user_id}") as r:
                    res = await r.json()
            data = base64.b64decode(res['properties'][0]['value'])
            data = json.loads(data)
            skin = data['textures']['SKIN']['url']
            embed = discord.Embed(color=0xDEADBF, title=f"User: {res['name']}")
            embed.set_image(url=skin)
            await ctx.send(embed=embed)
        except:
            await ctx.send(_("**Failed to get user**"))

def setup(bot):
    bot.add_cog(Games(bot))
