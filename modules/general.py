from discord.ext import commands
import discord
import aiohttp
from bs4 import BeautifulSoup
import base64
import config
import random
from PIL import Image
from io import BytesIO
import datetime
import qrcode
from urllib.parse import quote_plus
import rethinkdb as r
from math import sqrt

from .utils import helpers, instance_tools, chat_formatting, paginator

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def anime(self, ctx, *, search: str):
        """Get Anime Stats"""
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.post("https://graphql.anilist.co", json={
                "query": helpers.anilist_query,
                "variables": {
                    "search": search
                }
            }) as res:
                data = await res.json()
        if data.get("errors", []):
            return await ctx.send("Error getting data from anilist: {}".format(data["errors"][0]["message"]))
        media = data["data"]["Page"]["media"]
        if not media:
            return await ctx.send("Nothing found.")
        media = media[0]
        if media["isAdult"] is True and not ctx.channel.is_nsfw():
            return await ctx.send("NSFW Anime can't be displayed in non NSFW channels.")
        color = int(media["coverImage"]["color"].replace("#", ""), 16) if media["coverImage"]["color"] else 0xdeadbf
        em = discord.Embed(colour=color)
        em.title = "{} ({})".format(media["title"]["romaji"], media["title"]["english"])
        if media["description"]:
            desc = BeautifulSoup(media["description"], "lxml")
            if desc:
                em.description = desc.text
        em.url = "https://anilist.co/anime/{}".format(media["id"])
        em.set_thumbnail(url=media["coverImage"]["extraLarge"])
        em.add_field(name="Status", value=media["status"].title(), inline=True)
        em.add_field(name="Episodes", value=media["episodes"], inline=True)
        em.add_field(name="Score", value=str(media["averageScore"]), inline=True)
        em.add_field(name="Genres", value=", ".join(media["genres"]))
        dates = "{}/{}/{}".format(media["startDate"]["day"], media["startDate"]["month"], media["startDate"]["year"])
        if media["endDate"]["year"] is not None:
            dates += " - {}/{}/{}".format(media["endDate"]["day"], media["endDate"]["month"], media["endDate"]["year"])
        em.add_field(name="Date", value=dates)
        await ctx.send(embed=em)

    def whatanime_embedbuilder(self, doc: dict):
        em = discord.Embed(color=0xDEADBF)
        em.title = doc["title_romaji"]
        em.url = "https://myanimelist.net/anime/{}".format(doc["mal_id"])
        em.add_field(name="Episode", value=str(doc["episode"]))
        em.add_field(name="At", value=str(doc["at"]))
        em.add_field(name="Matching %", value=str(round(doc["similarity"] * 100, 2)))
        em.add_field(name="Native Title", value=doc["title_native"])
        em.set_footer(text="Powered by trace.moe")
        return em

    def whatanime_prefbuilder(self, doc):
        preview = f"https://trace.moe/thumbnail.php?anilist_id={doc['anilist_id']}" \
                  f"&file={doc['filename']}" \
                  f"&t={doc['at']}" \
                  f"&token={doc['tokenthumb']}"
        return preview

    @commands.command()
    @commands.cooldown(2, 25, commands.BucketType.user)
    @commands.guild_only()
    async def whatanime(self, ctx):
        """Check what the anime is from an image."""

        if not len(ctx.message.attachments) == 0:
            img = ctx.message.attachments[0].url
        else:
            def check(m):
                return m.channel == ctx.message.channel and m.author == ctx.message.author

            try:
                await ctx.send("Send me an image of an anime to search for.")
                x = await self.bot.wait_for('message', check=check, timeout=15)
            except:
                return await ctx.send("Timed out.")

            if not len(x.attachments) >= 1:
                return await ctx.send("You didn't give me a image.")

            img = x.attachments[0].url

        async with aiohttp.ClientSession() as cs:
            async with cs.get(img) as r:
                res = await r.read()

        with Image.open(BytesIO(res)) as img:
            img.seek(0)
            img.convert("RGB")
            img.thumbnail((512, 288), Image.ANTIALIAS)
            i = BytesIO()
            img.save(i, format="PNG")
            i.seek(0)

        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.post("https://trace.moe/api/search?token={}".format(config.whatanime),
                               data={"image": str(base64.b64encode(i.read()).decode("utf8"))},
                               headers={"Content-Type": "application/x-www-form-urlencoded"}) as r:
                if r.status == 503:
                    return await ctx.send("Service down for maintenance")
                try:
                    res = await r.json()
                except:
                    return await ctx.send("File too large.")

        if not res["docs"]:
            return await ctx.send("Nothing found.")

        doc = res["docs"][0]
        if doc["is_adult"] and not ctx.channel.is_nsfw:
            return await ctx.send("Can't send NSFW in a non NSFW channel.")

        em = self.whatanime_embedbuilder(doc)

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(self.whatanime_prefbuilder(doc)) as r:
                    imres = await r.read()
            file = discord.File(imres, filename="file.gif")
            em.set_image(url="attachment://file.gif")
        except:
            file = None
            em.set_image(url="https://nekobot.xyz/placeholder.png")

        await ctx.send(embed=em, file=file)

    @commands.command()
    async def cookie(self, ctx, user: discord.Member):
        """Give somebody a cookie :3"""
        await ctx.send("<:NekoCookie:408672929379909632> - **{} gave {} a cookie OwO** -"
                         " <:NekoCookie:408672929379909632>".format(ctx.message.author.name, user.mention))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def choose(self, ctx, *items):
        """Choose between multiple options"""
        if not items:
            return await ctx.send_help(ctx.command)
        await ctx.send("I chose: **{}**!".format(helpers.clean_text(random.choice(items))))

    def get_bot_uptime(self, *, brief=False):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
            else:
                fmt = '{h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h}h {m}m {s}s'
            if days:
                fmt = '{d}d ' + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx):
        """Get Bot's Info"""
        await ctx.trigger_typing()

        i = instance_tools.InstanceTools(self.bot.instances, self.bot.redis)
        servers = await i.get_all_guilds()
        members = await i.get_all_users()
        channels = await i.get_all_channels()

        if isinstance(ctx.channel, discord.TextChannel):
            thisShard = ctx.guild.shard_id
        else:
            thisShard = 0

        # len(self.bot.lavalink.players.find_all(lambda p: p.is_playing))
        info = discord.Embed(color=0xDEADBF, title="**Info**")
        info.description = "Servers: **{} ({})**\nMembers: **{}**\nBot Commands: **{}**\nChannels: **{}**\nShards: **{}**\nThis Shard: **{}**\nBot in voice channel(s): **{}**\nUptime: **{}**\n".format(
            helpers.millify(servers), servers,
            helpers.millify(members),
            str(len(self.bot.commands)),
            helpers.millify(channels),
            self.bot.shard_count,
            thisShard,
            0,
            self.get_bot_uptime()
        )
        info.add_field(name="Links",
                       value="[GitHub](https://github.com/hibikidesu/NekoBotRewrite/) | "
                               "[Support Server](https://discord.gg/q98qeYN) | "
                               "[Patreon](https://www.patreon.com/NekoBot)")
        info.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        await ctx.send(embed=info)

    @commands.command(aliases=["user"])
    @commands.guild_only()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def userinfo(self, ctx, user: discord.Member = None):
        """Get a users info."""

        if not user:
            user = ctx.message.author
        try:
            playinggame = user.activity.title
        except:
            playinggame = None

        server = ctx.message.guild
        embed = discord.Embed(color=0xDEADBF)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Discriminator", value=user.discriminator)
        embed.add_field(name="Bot", value=str(user.bot))
        embed.add_field(name="Created", value=user.created_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name="Joined", value=user.joined_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name="Animated Avatar", value=str(user.is_avatar_animated()))
        embed.add_field(name="Playing", value=playinggame)
        embed.add_field(name="Status", value=user.status)
        embed.add_field(name="Color", value=str(user.color))

        try:
            roles = [x.name for x in user.roles if x.name != "@everyone"]

            if roles:
                roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                           if x.name != "@everyone"].index)
                roles = ", ".join(roles)
            else:
                roles = "None"
            embed.add_field(name="Roles", value=roles)
        except:
            pass

        await ctx.send(embed=embed)

    @commands.command(aliases=["server"])
    @commands.guild_only()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def serverinfo(self, ctx):
        """Display Server Info"""
        server = ctx.guild
        verif = server.verification_level

        online = len([m.status for m in server.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])

        embed = discord.Embed(color=0xDEADBF)
        embed.add_field(name="Name", value=f"**{server.name}**\n({server.id})")
        embed.add_field(name="Owner", value=server.owner)
        embed.add_field(name="Online (Cached)", value=f"**{online}/{server.member_count}**")
        embed.add_field(name="Created at", value=server.created_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name="Channels", value=f"Text Channels: **{len(server.text_channels)}**\n"
        f"Voice Channels: **{len(server.voice_channels)}**\n"
        f"Categories: **{len(server.categories)}**\n"
        f"AFK Channel: **{server.afk_channel}**")
        embed.add_field(name="Roles", value=str(len(server.roles)))
        embed.add_field(name="Emojis", value=f"{len(server.emojis)}/100")
        embed.add_field(name="Region", value=str(server.region).title())
        embed.add_field(name="Security", value=f"Verification Level: **{verif}**\n"
        f"Content Filter: **{server.explicit_content_filter}**")

        try:
            embed.set_thumbnail(url=server.icon_url)
        except:
            pass

        await ctx.send(embed=embed)

    @commands.command(aliases=["channel"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        """Get Channel Info"""

        if channel is None:
            channel = ctx.message.channel

        embed = discord.Embed(color=0xDEADBF, description=channel.mention)
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="Server", value=channel.guild)
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="Category ID", value=channel.category_id)
        embed.add_field(name="Position", value=channel.position)
        embed.add_field(name="NSFW", value=str(channel.is_nsfw()))
        embed.add_field(name="Members (cached)", value=str(len(channel.members)))
        embed.add_field(name="Category", value=channel.category)
        embed.add_field(name="Created", value=channel.created_at.strftime("%d %b %Y %H:%M"))

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def urban(self, ctx, *, search_terms: str, definition_number: int = 1):
        """Search Urban Dictionary"""

        if not ctx.channel.is_nsfw():
            return await ctx.send("Please use this in an NSFW channel.", delete_after=5)

        def encode(s):
            return quote_plus(s, encoding="utf-8", errors="replace")

        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11):
                pos = 0
        except ValueError:
            pos = 0

        search_terms = "+".join([encode(s) for s in search_terms])
        url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    result = await r.json()
            if result["list"]:
                definition = result['list'][pos]['definition']
                example = result['list'][pos]['example']
                defs = len(result['list'])
                msg = ("**Definition #{} out of {}:\n**{}\n\n"
                       "**Example:\n**{}".format(pos + 1, defs, definition,
                                                 example))
                msg = chat_formatting.pagify(msg, ["\n"])
                for page in msg:
                    await ctx.send(page)
            else:
                await ctx.send("Your search terms gave no results.")
        except IndexError:
            await ctx.send("There is no definition #{}".format(pos + 1))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx, user: discord.Member = None, format_type: str = None):
        """Get a user's avatar"""
        await ctx.channel.trigger_typing()

        if user is None:
            user = ctx.message.author
        try:
            color = await helpers.get_dominant_color(self.bot, user.avatar_url_as(format="png"))
        except:
            color = 0xDEADBF
        em = discord.Embed(color=color, title="{}'s Avatar".format(user.name))
        if format_type is None or format_type not in ["png", "jpg", "gif", "jpeg", "webp"]:
            await ctx.send(embed=em.set_image(url=user.avatar_url))
        else:
            await ctx.send(embed=em.set_image(url=user.avatar_url_as(format=format_type)))

    @commands.command()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def coffee(self, ctx):
        """Coffee owo"""
        await ctx.channel.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekobot.xyz/api/image?type=coffee") as res:
                imgdata = await res.json()
            em = discord.Embed()
            msg = await ctx.send("*drinks coffee*", embed=em.set_image(url=imgdata["message"]))
            color = await helpers.get_dominant_color(self.bot, imgdata["message"])
            em = discord.Embed(color=color)
            await msg.edit(embed=em.set_image(url=imgdata["message"]))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def animepic(self, ctx):
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekobot.xyz/api/v2/image/animepic") as r:
                res = await r.json()
        image = res["message"]
        color = await helpers.get_dominant_color(self.bot, image)
        em = discord.Embed(color=color)
        await ctx.send(embed=em.set_image(url=image))

    @commands.command()
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def qr(self, ctx, *, message: str):
        """Generate a QR Code"""
        temp = BytesIO()
        qrcode.make(message).save(temp)
        temp.seek(0)
        await ctx.send(file=discord.File(temp, filename="qr.png"))

    @commands.command(aliases=["perms"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def permissions(self, ctx, user: discord.Member = None, channel: str = None):
        """Get Permissions,

        Example Usage:
            n!permissions/n!perms @ひびき#0001 testing
        or
            n!permissions/n!perms ひびき#0001 #testing"""

        if user is None:
            user = ctx.message.author

        if channel is None:
            channel = ctx.message.channel
        else:
            channel = discord.utils.get(ctx.message.guild.channels, name=channel)

        msg = "Perms for {} in {}: \n".format(user.name.replace("@", "@\u200B"), channel.name.replace("@", "@\u200B"))

        try:
            perms = user.permissions_in(channel)
            msg += ", ".join([x[0].replace("_", " ").title() for x in perms if x[1]])
            await ctx.send(msg)
        except:
            await ctx.send("Problem getting that channel...")

    @commands.command(aliases=["8"], name="8ball")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _8ball(self, ctx, *, question: str):
        """Ask 8Ball a question"""
        answers = ["<:online:313956277808005120> It is certain", "<:online:313956277808005120> As I see it, yes",
                   "<:online:313956277808005120> It is decidedly so", "<:online:313956277808005120> Most likely",
                   "<:online:313956277808005120> Without a doubt", "<:online:313956277808005120> Outlook good",
                   "<:online:313956277808005120> Yes definitely", "<:online:313956277808005120> Yes",
                   "<:online:313956277808005120> You may rely on it", "<:online:313956277808005120> Signs point to yes",
                   "<:away:313956277220802560> Reply hazy try again", "<:away:313956277220802560> Ask again later",
                   "<:away:313956277220802560> Better not tell you now",
                   "<:away:313956277220802560> Cannot predict now",
                   "<:away:313956277220802560> Concentrate and ask again",
                   "<:dnd:313956276893646850> Don't count on it",
                   "<:dnd:313956276893646850> My reply is no", "<:dnd:313956276893646850> My sources say no",
                   "<:dnd:313956276893646850> Outlook not so good", "<:dnd:313956276893646850> Very doubtful"]
        await ctx.send(embed=discord.Embed(title=random.choice(answers), color=0xDEADBF))

    @commands.command()
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def botinfo(self, ctx, bot_user: discord.Member):
        """Get a Bots Info"""
        if bot_user == None:
            bot_user = self.bot.user
        await ctx.trigger_typing()

        url = "https://discord.bots.gg/api/v1/bots/{}".format(bot_user.id)
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers={"Authorization": config.dpw_key}) as r:
                if r.status == 404:
                    return await ctx.send("Thats not a valid bot")
                bot = await r.json()
        try:
            em = discord.Embed(color=0xDEADBF)
            em.title = bot_user.name + "#" + bot_user.discriminator
            em.description = bot["shortDescription"]
            em.add_field(name="Prefix", value=bot.get("prefix", "None"))
            em.add_field(name="Lib", value=bot.get("libraryName"))
            em.add_field(name="Owners", value="{}#{}".format(bot["owner"]["username"], bot["owner"]["discriminator"]))
            em.add_field(name="ID", value=bot.get("clientId"))
            em.add_field(name="Website", value=bot.get("website") if bot.get("website") != "" else "None")
            em.set_thumbnail(url=bot_user.avatar_url_as(format="png"))
            await ctx.send(embed=em)
        except:
            return await ctx.send("Failed to get bot data.")

    @commands.group(hidden=True)
    @commands.is_owner()
    async def config(self, ctx):
        """Configuration"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @config.command(name="addbalance", hidden=True)
    @commands.is_owner()
    async def conf_add_balance(self, ctx, userid: int, amount: int):
        """Add balance to a user"""
        if not await r.table("economy").get(str(userid)).run(self.bot.r_conn):
            return await ctx.send("This user has no account.")
        u = await r.table("economy").get(str(userid)).run(self.bot.r_conn)
        balance = u["balance"]
        newbalance = balance + amount
        await r.table("economy").get(str(userid)).update({"balance": newbalance}).run(self.bot.r_conn)
        await ctx.send("Updated balance, user now has `{}`".format(newbalance))

    @config.command(name="createaccount", hidden=True)
    @commands.is_owner()
    async def conf_create_account(self, ctx, userid: int):
        """Create an account for a user"""
        if await r.table("economy").get(str(userid)).run(self.bot.r_conn):
            return await ctx.send("This user already has an account.")
        data = {
            "id": str(userid),
            "balance": 0,
            "lastpayday": "0",
            "bettimes": [],
            "frozen": False
        }
        await r.table("economy").insert(data).run(self.bot.r_conn)
        await ctx.send("Account created!")

    @config.command(name="avatar", hidden=True)
    @commands.is_owner()
    async def conf_avatar(self, ctx, *, avatar_url: str):
        """Change bots avatar"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(avatar_url) as r:
                res = await r.read()
        await self.bot.user.edit(avatar=res)
        try:
            emoji = self.bot.get_emoji(408672929379909632)
            await ctx.message.add_reaction(emoji)
        except:
            pass

    @config.command(name="username", hidden=True)
    @commands.is_owner()
    async def conf_name(self, ctx, *, name: str):
        """Change bots username"""
        await self.bot.user.edit(username=name)
        try:
            emoji = self.bot.get_emoji(408672929379909632)
            await ctx.message.add_reaction(emoji)
        except:
            pass

    @config.command(hidden=True, name="blacklist")
    @commands.is_owner()
    async def conf_blacklist(self, ctx, userid):
        """Blacklist user from levelling"""
        userdata = await r.table("levelSystem").get(str(userid)).run(self.bot.r_conn)
        if userdata["blacklisted"]:
            await r.table("levelSystem").get(str(userid)).update({"blacklisted": False}).run(self.bot.r_conn)
            await ctx.send("Removed from blacklist")
        else:
            await r.table("levelSystem").get(str(userid)).update({"blacklisted": True}).run(self.bot.r_conn)
            await ctx.send("Added to blacklist")

    @config.command(hidden=True, name="reset")
    @commands.is_owner()
    async def conf_reset(self, ctx, userid: int):
        """Reset user"""
        await r.table("levelSystem").get(str(userid)).update({"xp": 0, "lastxptimes": [], "lastxp": "0"}).run(
            self.bot.r_conn)
        await ctx.send("Reset user.")

    @config.command(hidden=True, name="freeze")
    @commands.is_owner()
    async def conf_freeze(self, ctx, userid: int):
        """Freeze users from eco"""
        data = await r.table("economy").get(str(userid)).run(self.bot.r_conn)
        if data["frozen"]:
            await r.table("economy").get(str(userid)).update({"frozen": False}).run(self.bot.r_conn)
            await ctx.send("Unfroze user")
        else:
            await r.table("economy").get(str(userid)).update({"frozen": True}).run(self.bot.r_conn)
            await ctx.send("Froze user")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def getuser(self, ctx, userid: int):
        """Get user from id"""
        try:
            user = await self.bot.fetch_user(userid)
            created_at = user.created_at.strftime("%d %b %Y %H:%M")
            bank = await r.table("economy").get(str(userid)).run(self.bot.r_conn)
            level = await r.table("levelSystem").get(str(userid)).run(self.bot.r_conn)

            em = discord.Embed(color=0xDEADBF)
            em.set_author(name=str(user), icon_url=user.avatar_url)
            em.add_field(name="Bot?", value=str(user.bot))
            em.add_field(name="Created At", value=str(created_at))
            if bank:
                em.add_field(name="Balance", value=bank["balance"])
                em.add_field(name="Last Payday", value=bank["lastpayday"])
            if level:
                em.add_field(name="XP", value=str(level["xp"]))
                em.add_field(name="Level", value=str(int((1 / 278) * (9 + sqrt(81 + 1112 * (level["xp"]))))))
                em.add_field(name="Blacklisted?", value=str(level["blacklisted"]))
                em.add_field(name="Last XP", value=level["lastxp"])
            await ctx.send(embed=em)
        except:
            await ctx.send("Failed to find user.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shorten(self, ctx, *, url: str):
        """Shorten a URL"""
        url = f"https://api-ssl.bitly.com/v3/shorten?access_token={config.bitly}&longUrl={url}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        if res["status_code"] != 200:
            em = discord.Embed(color=0xDEADBF, title="Error",
                               description="Error: {}\nMake sure the URL starts with http(s)://".format(res["status_txt"]))
            return await ctx.send(embed=em)
        em = discord.Embed(color=0xDEADBF, title="Shortened URL", description=res["data"]["url"])
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        """Get the bots invite"""
        await ctx.send("**Invite the bot:** <https://uwu.whats-th.is/32dde7>\n**Support Server:** <https://discord.gg/q98qeYN>")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def prefix(self, ctx):
        """Get the bots current prefix."""
        currprefix = await self.bot.redis.get(f"{ctx.author.id}-prefix")

        if currprefix:
            currprefix = currprefix.decode("utf8")
            await ctx.send("Your custom prefix is set to `{}`".format(currprefix))
        else:
            await ctx.send("My prefix is `n!` or `N!`")

    @commands.command(aliases=["deleteprefix", "resetprefix"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def delprefix(self, ctx):
        """Delete or reset your prefix"""
        await self.bot.redis.delete(f"{ctx.author.id}-prefix")
        await ctx.send("Deleted your prefix and reset it back to the default `n!`")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setprefix(self, ctx, prefix: str):
        """Set your custom prefix, use quotation marks like "baka " for spaces."""
        if len(prefix) >= 12:
            return await ctx.send("Your prefix is over 12 characters.")
        await self.bot.redis.set(f"{ctx.author.id}-prefix", prefix)
        await ctx.send("Set **your** custom prefix to `{}`, you can remove it by pinging me and using delprefix.".format(helpers.clean_text(prefix)))

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.guild)
    async def help(self, ctx, command: str = None):
        """Help!"""
        if command:
            entity = self.bot.get_cog(command) or self.bot.get_command(command)

            if entity:
                if isinstance(entity, commands.Command):
                    p = await paginator.HelpPaginator.from_command(ctx, entity)
                else:
                    p = await paginator.HelpPaginator.from_cog(ctx, entity)
                return await p.paginate()
        try:
            other = ""
            other += "`pet`, "
            other += "`card`, "
            other += "`imgwelcome`, "
            other += ", ".join([f"`{i.name}`" for i in self.bot.cogs["Marriage"].get_commands()])
            embed = discord.Embed(color=0xDEADBF, title="NekoBot Help")
            c = [cog for cog in self.bot.cogs if cog not in ["NekoPet", "CardGame", "IMGWelcome", "Marriage"]]
            c.sort()
            for x in c:
                if x == "NSFW" and isinstance(ctx.channel, discord.TextChannel) and not ctx.channel.is_nsfw():
                    embed.add_field(name="NSFW",
                                    value="Hidden in non NSFW channel, you can enable NSFW channels by using `n!nsfw` or going in the channels settings <a:bearCop:457881833191768066>",
                                    inline=False)
                else:
                    try:
                        embed.add_field(name=x.title(),
                                        value=", ".join(["`{}`".format(cmd.name) for cmd in self.bot.cogs[x].get_commands() if not cmd.hidden]),
                                        inline=False)
                    except:
                        pass
            embed.add_field(name="Other", value=other, inline=False)
            await ctx.send(embed=embed)
        except discord.HTTPException:
            return await ctx.send("**I can't send embeds.**")
        try:
            emoji = self.bot.get_emoji(462373594555613214)
            await ctx.message.add_reaction(emoji)
        except:
            pass

def setup(bot):
    bot.add_cog(General(bot))
