from discord.ext import commands
import discord, config, aiohttp
import base64
import json
import gettext

wargaming = {
    "wows": {
        "servers": {
            "ru": "https://api.worldofwarships.ru/wows/",
            "eu": "https://api.worldofwarships.eu/wows/",
            "na": "https://api.worldofwarships.com/wows/",
            "asia": "https://api.worldofwarships.asia/wows/"
        },
        "nations": {
            "commonwealth": "🇦🇺 ",
            "italy": "🇮🇹 ",
            "usa": "🇺🇸 ",
            "pan_asia": "🇨🇳 ",
            "france": "🇫🇷 ",
            "ussr": "☭ ",
            "germany": "🇩🇪 ",
            "uk": "🇬🇧 ",
            "japan": "🇯🇵 ",
            "poland": "🇵🇱 ",
            "pan_america": ""
        }
    }
}

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

    async def wows_get_user(self, username, region):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    wargaming["wows"]["servers"][region] + "account/list/?application_id=" + config.wargaming_id + "&search=" + username
            ) as r:
                res = await r.json()
        return res.get("data", [])

    async def wows_get_ship(self, ship_id, session: aiohttp.ClientSession):
        cache = await self.bot.redis.get("ship:%s" % ship_id)
        if not cache:
            async with session.get(
                "https://api.worldofwarships.com/wows/encyclopedia/ships/?application_id=%s&ship_id=%s&language=en" % (
                    config.wargaming_id, ship_id
                )
            ) as r:
                res = await r.json()
            data = res["data"][str(ship_id)]
            await self.bot.redis.set("ship:%s" % ship_id, json.dumps(data))
            return data
        else:
            return json.loads(cache)

    @commands.group()
    @commands.guild_only()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def wows(self, ctx):
        """World of Warships"""
        if ctx.invoked_subcommand is None:
            return await self.bot.send_cmd_help(ctx)

    @wows.command(name="ships")
    async def wows_ships(self, ctx, username: str, region: str = "na"):
        """Get a users ships"""
        await ctx.trigger_typing()
        region = region.lower()
        if region not in list(wargaming["wows"]["servers"]):
            return await ctx.send("Not a valid region, valid regions: %s" % ", ".join(list(wargaming["wows"]["servers"])))
        user = await self.wows_get_user(username, region)
        if not user:
            return await ctx.send("No users found")
        user = user[0]
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                wargaming["wows"]["servers"][region] + "ships/stats/?application_id=%s&account_id=%s" % (config.wargaming_id, user["account_id"])
            ) as r:
                res = await r.json()
        msg = "Displaying **%s's** Top 10 Ships:\n" % user["nickname"]
        async with aiohttp.ClientSession() as cs:
            for ship in sorted(res["data"][str(user["account_id"])], reverse=True, key=lambda i: i["pvp"]["xp"])[:10]:
                ship_data = await self.wows_get_ship(ship["ship_id"], cs)
                msg += "    - **%s%s:**\n" % (wargaming["wows"]["nations"][ship_data["nation"]], ship_data["name"])
                msg += "        - Type: %s\n        - Battles: %s (%s Wins, %s Loses)\n        - Kills: %s\n" \
                       "        - Total XP: %s\n" % (
                    ship_data["type"],
                    ship["pvp"]["battles"],
                    ship["pvp"]["wins"],
                    ship["pvp"]["losses"],
                    ship["pvp"]["frags"],
                    ship["pvp"]["xp"]
                )
        await ctx.send(msg)

    @wows.command(name="user")
    async def wows_user(self, ctx, username: str, region: str = "na"):
        """Get user stats"""
        await ctx.trigger_typing()
        region = region.lower()
        if region not in list(wargaming["wows"]["servers"]):
            return await ctx.send("Not a valid region, valid regions: %s" % ", ".join(list(wargaming["wows"]["servers"])))
        user_id = await self.wows_get_user(username, region)
        if not user_id:
            return await ctx.send("No users found")
        user_id = user_id[0]["account_id"]
        async with aiohttp.ClientSession() as cs:
            async with cs.get(wargaming["wows"]["servers"][region] + "account/info/?application_id=%s&account_id=%s" % (
                    config.wargaming_id, user_id
            )) as r:
                res = await r.json()
        user_data = res["data"][str(user_id)]
        msg = ""
        msg += "**%s** - Lvl. **%s**\n\n" % (user_data["nickname"], user_data["leveling_tier"])
        msg += "**Battles:**\n"
        msg += "    - Total Battles: %s\n    - Wins: %s\n    - Loses: %s\n    - Draws: %s\n" % (
            user_data["statistics"]["pvp"]["battles"],
            user_data["statistics"]["pvp"]["wins"],
            user_data["statistics"]["pvp"]["losses"],
            user_data["statistics"]["pvp"]["draws"]
        )
        msg += "**Main Battery:**\n"
        msg += "    - Max Kills in Battle: %s\n    - Kills: %s\n    - Hits: %s\n    - Shots: %s\n" % (
            user_data["statistics"]["pvp"]["main_battery"]["max_frags_battle"],
            user_data["statistics"]["pvp"]["main_battery"]["frags"],
            user_data["statistics"]["pvp"]["main_battery"]["hits"],
            user_data["statistics"]["pvp"]["main_battery"]["shots"]
        )
        msg += "**Second Battery:**\n"
        msg += "    - Max Kills in Battle: %s\n    - Kills: %s\n    - Hits: %s\n    - Shots: %s\n" % (
            user_data["statistics"]["pvp"]["second_battery"]["max_frags_battle"],
            user_data["statistics"]["pvp"]["second_battery"]["frags"],
            user_data["statistics"]["pvp"]["second_battery"]["hits"],
            user_data["statistics"]["pvp"]["second_battery"]["shots"]
        )
        msg += "**Torpedoes:**\n"
        msg += "    - Max Kills in Battle: %s\n    - Kills: %s\n    - Hits: %s\n    - Shots: %s\n" % (
            user_data["statistics"]["pvp"]["torpedoes"]["max_frags_battle"],
            user_data["statistics"]["pvp"]["torpedoes"]["frags"],
            user_data["statistics"]["pvp"]["torpedoes"]["hits"],
            user_data["statistics"]["pvp"]["torpedoes"]["shots"]
        )
        msg += "**Other:**\n"
        msg += "    - Total Distance Travelled: %s Miles (%s Kilometers)\n    - Ships Spotted: %s\n" \
               "    - Survived Battles: %s\n    - Kills: %s\n    - Planes Killed: %s\n" % (
                   user_data["statistics"]["distance"], round(user_data["statistics"]["distance"] * 1.609),
                   user_data["statistics"]["pvp"]["ships_spotted"],
                   user_data["statistics"]["pvp"]["survived_battles"],
                   user_data["statistics"]["pvp"]["frags"],
                   user_data["statistics"]["pvp"]["planes_killed"]
               )
        if user_data["statistics"]["pvp"]["max_frags_ship_id"]:
            async with aiohttp.ClientSession() as cs:
                msg += "    - Most Kills With: %s\n" % (
                    (await self.wows_get_ship(user_data["statistics"]["pvp"]["max_frags_ship_id"], cs))["name"]
                )
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Games(bot))
