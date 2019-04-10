from discord.ext import commands
import discord, config, aiohttp
import base64
import json
from PIL import Image, ImageFont, ImageDraw
from modules.eco import interpolate, get_rgb
from io import BytesIO
import time
import random
from .utils.helpers import get_dominant_color

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

osu_icons = ["osu", "taiko", "ctb", "mania"]
__gradients = [
    ["fad0c4", "ff9a9e"],
    ["333333", "dd1818"],
    ["11998e", "38ef7d"],
    ["108dc7", "ef8e38"],
    ["FC5C7D", "6A82FB"],
    ["FC466B", "3F5EFB"],
    ["c94b4b", "4b134f"],
    ["23074d", "cc5333"],
    ["fffbd5", "b20a2c"],
    ["00b09b", "96c93d"],
    ["D3CCE3", "E9E4F0"],
    ["800080", "ffc0cb"],
    ["00F260", "0575E6"],
    ["fc4a1a", "f7b733"],
    ["74ebd5", "ACB6E5"],
    ["22c1c3", "fdbb2d"],
    ["ff9966", "ff5e62"],
    ["7F00FF", "E100FF"],
    ["d9a7c7", "fffcdc"],
    ["EF3B36", "FFFFFF"],
    ["56CCF2", "2F80ED"],
    ["F2994A", "F2C94C"],
    ["30E8BF", "FF8235"],
    ["4568DC", "B06AB3"],
    ["43C6AC", "F8FFAE"]
]

def get_random_gradients():
    a, b = random.choice(__gradients)
    return get_rgb(a), get_rgb(b)

class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def osu(self, ctx):
        """osu UwU"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    async def osu_converter(self, ctx: commands.Context, arg: str):
        converter = commands.MemberConverter()
        try:
            user = await converter.convert(ctx, arg)
            data = await self.bot.redis.get("osu:{}".format(user.id))
            if data is None:
                raise ValueError("Missing data")
            data = int(data)
            return data
        except:
            return arg

    def NoneRemover(self, arg, value):
        if arg is None:
            return value
        return arg

    async def generate_card(self, data: dict, game: int):
        # Sweat, messy
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://a.ppy.sh/{}_{}.png".format(data.get("user_id", ""), int(time.time()))) as res:
                avatar = BytesIO((await res.read()))

        img = Image.new("RGBA", (450, 125), (0, 0, 0, 0))
        front = Image.new("RGBA", (440, 115), (255, 255, 255, 255))
        draw = ImageDraw.Draw(front)
        g1, g2 = get_random_gradients()
        for x, color in enumerate(interpolate(g1, g2, img.size[1] * 5)):
            draw.line((x, 0, 0, x), tuple(color), 1)
        avatar = Image.open(avatar).resize((101, 101), Image.ANTIALIAS)
        triangles = Image.open("data/osu/triangles.png").resize((440, 105), Image.ANTIALIAS)
        triangles.putalpha(16)
        front.alpha_composite(triangles, (0, 0))
        txt = "#{:,}".format(int(self.NoneRemover(data.get("pp_rank", 0), 0)))
        draw.text((376 - (len(txt) * 10), 20), txt, (255, 255, 255), ImageFont.truetype("data/osu/exo2regular.ttf", 19))
        draw.text((115, 10), data.get("username", ""), (255, 255, 255),
                  ImageFont.truetype("data/osu/exo2medium.ttf", 28 if len(data.get("username", "")) <= 8 else 26))
        back = Image.new("RGBA", (432, 64), (255, 255, 255, 255))
        draw = ImageDraw.Draw(back)
        side_num_fnt = ImageFont.truetype("data/osu/exo2bold.ttf", 18)
        draw.text((110, 5), "Accuracy", (110, 110, 110), ImageFont.truetype("data/osu/exo2regular.ttf", 20))
        draw.text((110, 27), "Play Count", (110, 110, 110), ImageFont.truetype("data/osu/exo2regular.ttf", 18))
        draw.text((360, 6), "{}%".format(round(float(self.NoneRemover(data.get("accuracy", 0.0), 0)), 2)), (90, 90, 90), side_num_fnt)
        txt = "{:,} (lvl{})".format(int(self.NoneRemover(data.get("playcount", 0), 0)), round(float(self.NoneRemover(data.get("level", 0), 0))))
        draw.text((445 - (len(txt) * 10), 24), txt, (90, 90, 90), side_num_fnt)
        try:
            flag = Image.open("data/osu/flags/{}.png".format(data.get("country", "JP"))).convert("RGBA").resize((24, 16), Image.ANTIALIAS)
        except:
            flag = Image.open("data/osu/flags/{}.png".format("JP")).convert("RGBA").resize((24, 16), Image.ANTIALIAS)
        game = Image.open("data/osu/{}.png".format(osu_icons[game])).resize((16, 16), Image.ANTIALIAS)
        front.alpha_composite(game, (383, 24))
        front.alpha_composite(flag, (405, 24))
        front.alpha_composite(back, (5, 48))
        front.paste(avatar, (8, 8))
        img.paste(front, (5, 5))
        temp = BytesIO()
        img.save(temp, format="png")
        temp.seek(0)

        img.close()
        front.close()
        avatar.close()
        triangles.close()
        back.close()
        flag.close()
        game.close()

        return temp

    @osu.command(name="link")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def osu_link(self, ctx):
        """Link your osu! account to your discord"""
        data = await self.bot.redis.get("osu:{}".format(ctx.author.id))
        if data is None:
            return await ctx.send("You can link your osu! account using this link, <https://osu.nekobot.xyz/>")
        await ctx.send("Your osu! account is already linked to your discord account, send `yes` if you would like to unlink it.")
        try:
            msg = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.message.channel and x.author == ctx.author, timeout=15.0)
            if msg.content.lower() != "yes":
                return
        except:
            return
        await self.bot.redis.delete("osu:{}".format(ctx.author.id))

    @osu.command(name="standard")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def osu_standard(self, ctx, user):
        """View osu!standard stats of a user"""
        user = await self.osu_converter(ctx, user)
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://osu.ppy.sh/api/get_user?k={}&u={}&m=0&type={}".format(
                config.osu_key,
                user,
                "id" if isinstance(user, int) else "string"
            )) as res:
                res = await res.json()
        if not res:
            return await ctx.send("No data found")
        data = res[0]
        await ctx.trigger_typing()
        await ctx.send(file=discord.File((await self.generate_card(data, 0)), "osu.png"))

    @osu.command(name="taiko")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def osu_taiko(self, ctx, user):
        """View osu!taiko stats of a user"""
        user = await self.osu_converter(ctx, user)
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://osu.ppy.sh/api/get_user?k={}&u={}&m=1&type={}".format(
                    config.osu_key,
                    user,
                    "id" if isinstance(user, int) else "string"
            )) as res:
                res = await res.json()
        if not res:
            return await ctx.send("No data found")
        data = res[0]
        await ctx.trigger_typing()
        await ctx.send(file=discord.File((await self.generate_card(data, 1)), "osu.png"))

    @osu.command(name="ctb")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def osu_ctb(self, ctx, user):
        """View osu!ctb stats of a user"""
        user = await self.osu_converter(ctx, user)
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://osu.ppy.sh/api/get_user?k={}&u={}&m=2&type={}".format(
                    config.osu_key,
                    user,
                    "id" if isinstance(user, int) else "string"
            )) as res:
                res = await res.json()
        if not res:
            return await ctx.send("No data found")
        data = res[0]
        await ctx.trigger_typing()
        await ctx.send(file=discord.File((await self.generate_card(data, 2)), "osu.png"))

    @osu.command(name="mania")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def osu_mania(self, ctx, user):
        """View osu!mania stats of a user"""
        user = await self.osu_converter(ctx, user)
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://osu.ppy.sh/api/get_user?k={}&u={}&m=3&type={}".format(
                    config.osu_key,
                    user,
                    "id" if isinstance(user, int) else "string"
            )) as res:
                res = await res.json()
        if not res:
            return await ctx.send("No data found")
        data = res[0]
        await ctx.trigger_typing()
        await ctx.send(file=discord.File((await self.generate_card(data, 3)), "osu.png"))

    @osu.command(name="beatmap")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def osu_beatmap(self, ctx, *, title: str):
        """Get details about a beatmap"""
        await ctx.trigger_typing()
        url = "https://osusearch.com/query/?title={}&statuses=Ranked,Qualified,Loved&query_order=play_count".format(title)
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as res:
                osusearch = json.loads((await res.read()))
            if not osusearch["beatmaps"]:
                return await ctx.send("No beatmaps found.")
            beatmap = osusearch["beatmaps"][0]
            async with cs.get("https://osu.ppy.sh/api/get_beatmaps?k={}&b={}".format(
                config.osu_key,
                beatmap["beatmap_id"]
            )) as res:
                beatmap_data = await res.json()
            if not beatmap_data:
                return await ctx.send("No data found.")
        beatmap_data = beatmap_data[0]
        image_url = "https://assets.ppy.sh/beatmaps/{}/covers/card.jpg?{}".format(beatmap_data["beatmapset_id"], int(time.time()))
        color = await get_dominant_color(self.bot, image_url)
        em = discord.Embed(colour=color, title="**{}** - {}".format(beatmap["title"], beatmap["artist"]))
        em.set_image(url=image_url)
        em.add_field(name="Length", value="{}s".format(beatmap_data["total_length"]))
        em.add_field(name="Mode", value=osu_icons[int(beatmap_data["mode"])])
        em.add_field(name="Creator", value=beatmap_data["creator"])
        em.add_field(name="BPM", value=beatmap_data["bpm"])
        em.add_field(name="Max Combo", value=beatmap_data["max_combo"])
        em.add_field(name="Difficulty", value=str(round(float(beatmap_data["difficultyrating"]))))
        em.add_field(name="Play Count", value=beatmap_data["playcount"])
        em.add_field(name="Users Passed", value=beatmap_data["passcount"])
        await ctx.send(embed=em)

    @osu.command(name="top")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def osu_top(self, ctx, gamemode: str):
        """Get top users of a gamemode"""
        if gamemode.lower() not in ["standard", "taiko", "ctb", "mania"]:
            return await ctx.send("Not a valid gamemode")
        for i, x, in enumerate(["standard", "taiko", "ctb", "mania"]):
            if x == gamemode.lower():
                gamemode = i
                break
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://osustats.ppy.sh/api/getScoreRanking?gamemode={}&page=1&rankMax=25&rankMin=1".format(gamemode)) as res:
                users = await res.json()
            async with cs.get("https://osustats.ppy.sh/api/getScoreRanking?gamemode={}&page=2&rankMax=25&rankMin=1".format(gamemode)) as res:
                users = users + (await res.json())
        message = "**Top users for osu!{}**\n".format(["standard", "taiko", "ctb", "mania"][gamemode])
        for i, user in enumerate(users, start=1):
            message += "**{}.** {}\n".format(i, user["osu_user"]["userName"])
        await ctx.send(message)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def minecraft(self, ctx, username:str):
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
            await ctx.send("**Failed to get user**")

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
            return await ctx.send_help(ctx.command)

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
