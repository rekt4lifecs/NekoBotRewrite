from discord.ext import commands
import discord
import datetime, random, config, math, aiohttp, psutil
from collections import Counter
from .utils.chat_formatting import pagify
from urllib.parse import quote_plus
import string, ujson
from .utils.paginator import EmbedPages, Pages, HelpPaginator
from scipy import stats
import numpy
from colorthief import ColorThief
from io import BytesIO
from .utils import instance_tools
import qrcode, os, uuid
import logging
import base64
from PIL import Image
import urllib
import rethinkdb as r

log = logging.getLogger()

LOWERCASE, UPPERCASE = 'x', 'X'
def triplet(rgb, lettercase=LOWERCASE):
    return format(rgb[0]<<16 | rgb[1]<<8 | rgb[2], '06'+lettercase)

class Discriminator(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            if not int(argument) in range(1, 10000):
                raise commands.BadArgument('That isn\'t a valid discriminator.')
        except ValueError:
            raise commands.BadArgument('That isn\'t a valid discriminator.')
        else:
            return int(argument)


class Selector(commands.Converter):
    async def convert(self, ctx, argument):
        if argument not in ['>', '>=', '<', '<=', '=']:
            raise commands.BadArgument('Not a valid selector')
        return argument

def millify(n):
    millnames = ['', 'k', 'M', ' Billion', ' Trillion']
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])

# Languages
languages = ["english", "weeb", "tsundere", "polish", "spanish", "french"]
lang = {}

for l in languages:
    with open("lang/%s.json" % l, encoding="utf-8") as f:
        lang[l] = ujson.load(f)

def getlang(la:str):
    return lang.get(la, None)

class General:
    """General Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()
        if not hasattr(bot, "games"):
            self.bot.games = Counter()

    async def on_socket_response(self, msg):
        self.bot.socket_stats[msg.get('t')] += 1

    @commands.command()
    @commands.cooldown(2, 45, commands.BucketType.user)
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
            img.convert("RGB")
            img.seek(0)
            img.resize((512, 288))
            i = BytesIO()
            img.save(i, format="PNG")
            i.seek(0)

        try:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.post("https://whatanime.ga/api/search?token=%s" % config.whatanime,
                                   data={"image": str(base64.b64encode(i.read()).decode("utf8"))},
                                   headers={"Content-Type": "application/x-www-form-urlencoded"}) as r:
                    try:
                        res = await r.json()
                    except:
                        return await ctx.send("File too large.")

            if res["docs"] == []:
                return await ctx.send("Nothing found.")

            doc = res["docs"][0]

            if doc["is_adult"] and not ctx.channel.is_nsfw:
                return await ctx.send("Can't send NSFW in a non NSFW channel.")

            em = discord.Embed(color=0xDEADBF)
            em.title = doc["title_romaji"]
            em.url = "https://myanimelist.net/anime/%s" % doc["mal_id"]
            em.add_field(name="Episode", value=str(doc["episode"]))
            em.add_field(name="At", value=str(doc["at"]))
            em.add_field(name="Matching %", value=str(round(doc["similarity"] * 100, 2)))
            em.add_field(name="Native Title", value=doc["title_native"])
            em.set_footer(text="Powered by whatanime.ga")

            try:
                preview = f"https://whatanime.ga/preview.php?anilist_id={doc['anilist_id']}" \
                          f"&file={urllib.parse.quote_plus(doc['filename'])}" \
                          f"&t={doc['at']}" \
                          f"&token={doc['tokenthumb']}"
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(preview) as r:
                        res = await r.read()

                file = discord.File(res, filename="file.gif")
                em.set_image(url="attachment://file.gif")
            except:
                return await ctx.send(embed=em)

            await ctx.send(embed=em, file=file)
        except Exception as e:
            return await ctx.send("Failed to get data, %s" % e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setlang(self, ctx, lang:str=None):
        """Change the bot language for you."""
        if lang is None:
            em = discord.Embed(color=0xDEADBF, title="Change Language.",
                               description="Usage: `n!setlang <language>`\n"
                                           "Example: `n!setlank english`\n"
                                           "\n"
                                           "List of current languages:\n"
                                           "`english`,\n"
                                           "`weeb`,\n"
                                           "`tsundere` - computerfreaker#4054\n"
                                           "`polish` - YebakazLLE#7118\n"
                                           "`spanish` - ΛTLΛS Dinoseto & Luketten\n"
                                           "`french` - ShiroNeko#7379 & Anderson")
            return await ctx.send(embed=em)
        if lang.lower() in languages:
            await self.bot.redis.set(f"{ctx.message.author.id}-lang", lang.lower())
            await ctx.send(f"Set language to {lang.title()}!")
        else:
            await ctx.send("Invalid language.")

    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms: str):
        """Creates a lmgtfy link"""
        search_terms = search_terms.replace(" ", "+")
        await ctx.send("https://lmgtfy.com/?q={}".format(search_terms))

    @commands.command(pass_context=True)
    async def cookie(self, ctx, user: discord.Member):
        """Give somebody a cookie :3"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        await ctx.send(getlang(lang)["general"]["cookie"].format(ctx.message.author.name, user.mention))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def choose(self, ctx, *items):
        """Choose between multiple options"""
        if not items:
            return await self.bot.send_cmd_help(ctx)
        await ctx.send("I chose: **%s**!" % (random.choice(items)).replace("@", "@\u200B"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def flip(self, ctx):
        """Flip a coin"""
        x = random.randint(0, 1)
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
            if x == 1:
                await ctx.send(getlang(lang)["general"]["flip"]["heads"], file=discord.File("data/heads.png"))
            else:
                await ctx.send(getlang(lang)["general"]["flip"]["tails"], file=discord.File("data/tails.png"))
        else:
            if x == 1:
                await ctx.send("**Heads**", file=discord.File("data/heads.png"))
            else:
                await ctx.send("**Tails**", file=discord.File("data/tails.png"))

    def id_generator(self, size=7, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

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

    @commands.command(aliases=['version'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def info(self, ctx):
        """Get Bot's Info"""
        await ctx.trigger_typing()

        i = instance_tools.InstanceTools(self.bot.instances, self.bot.redis)
        servers = await i.get_all_guilds()
        members = await i.get_all_users()
        channels = await i.get_all_channels()
        messages = await i.get_all_messages()
        command_count = await i.get_all_commands()

        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if isinstance(ctx.channel, discord.TextChannel):
            thisShard = ctx.guild.shard_id
        else:
            thisShard = 0

        info = discord.Embed(color=0xDEADBF,
                             title=getlang(lang)["general"]["info"]["info"],
                             description=getlang(lang)["general"]["info"]["stats"].format(millify(servers),
                                                                                          servers,
                                                                                          millify(members),
                                                                                          str(len(self.bot.commands)),
                                                                                          millify(channels),
                                                                                          self.bot.shard_count,
                                                                                          # len(self.bot.lavalink.players.find_all(lambda
                                                                                          #   p: p.is_playing))
                                                                                          0,
                                                                                          self.get_bot_uptime(),
                                                                                          millify(messages),
                                                                                          str(self.bot.command_usage.most_common(1)[0][0]),
                                                                                          command_count,
                                                                                          thisShard))
        info.add_field(name=getlang(lang)["general"]["info"]["links"]["name"],
                       value=getlang(lang)["general"]["info"]["links"]["links"])
        info.set_thumbnail(url=self.bot.user.avatar_url_as(format='png'))
        await ctx.send(embed=info)

    @commands.command(hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def socketstats(self, ctx):
        delta = datetime.datetime.utcnow() - self.bot.uptime
        minutes = delta.total_seconds() / 60
        total = sum(self.bot.socket_stats.values())
        cpm = total / minutes
        em = discord.Embed(color=0xDEADBF, title="Websocket Stats",
                           description=f'{total} socket events observed ({cpm:.2f}/minute):\n{self.bot.socket_stats}')
        await ctx.send(embed=em)

    @commands.command(aliases=["emojiinfo", "emote", "emoji"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def emoteinfo(self, ctx, emote:discord.Emoji):
        """Get Emote Info"""
        em = discord.Embed(color=0xDEADBF)
        em.add_field(name="Name", value=emote.name, inline=False)
        em.add_field(name="ID", value=emote.id, inline=False)
        em.add_field(name="Animated?", value=str(emote.animated), inline=False)
        guild = emote.guild
        em.add_field(name="Server", value=f"{guild.name} ({guild.id})", inline=False)
        em.set_thumbnail(url=emote.url)
        await ctx.send(embed=em)

    @commands.command(aliases=['user'])
    @commands.guild_only()
    async def userinfo(self, ctx, user: discord.Member = None):
        """Get a users info."""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if user == None:
            user = ctx.message.author
        try:
            playinggame = user.activity.title
        except:
            playinggame = None
        server = ctx.message.guild
        embed = discord.Embed(color=0xDEADBF)
        embed.set_author(name=user.name,
                         icon_url=user.avatar_url)
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["id"], value=user.id)
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["discrim"], value=user.discriminator)
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["bot"], value=str(user.bot))
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["created"], value=user.created_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["joined"], value=user.joined_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["animated_avatar"], value=str(user.is_avatar_animated()))
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["playing"], value=playinggame)
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["status"], value=user.status)
        embed.add_field(name=getlang(lang)["general"]["userinfo"]["color"], value=user.color)

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

    @commands.command(aliases=['server'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Display Server Info"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        server = ctx.message.guild

        verif = server.verification_level

        online = len([m.status for m in server.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])

        embed = discord.Embed(color=0xDEADBF)
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["name"], value=f"**{server.name}**\n({server.id})")
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["owner"], value=server.owner)
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["online"], value=f"**{online}/{len(server.members)}**")
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["created_at"], value=server.created_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["channels"], value=f"Text Channels: **{len(server.text_channels)}**\n"
                                               f"Voice Channels: **{len(server.voice_channels)}**\n"
                                               f"Categories: **{len(server.categories)}**\n"
                                               f"AFK Channel: **{server.afk_channel}**")
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["roles"], value=len(server.roles))
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["emojis"], value=f"{len(server.emojis)}/100")
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["region"], value=str(server.region).title())
        embed.add_field(name=getlang(lang)["general"]["serverinfo"]["security"], value=f"Verification Level: **{verif}**\n"
                                               f"Content Filter: **{server.explicit_content_filter}**")

        try:
            embed.set_thumbnail(url=server.icon_url)
        except:
            pass

        await ctx.send(embed=embed)

    @commands.command(aliases=['channel'])
    @commands.guild_only()
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        """Get Channel Info"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        if channel is None:
            channel = ctx.message.channel

        embed = discord.Embed(color=0xDEADBF,
                              description=channel.mention)
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["name"], value=channel.name)
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["guild"], value=channel.guild)
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["id"], value=channel.id)
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["category_id"], value=channel.category_id)
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["position"], value=channel.position)
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["nsfw"], value=str(channel.is_nsfw()))
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["members"], value=len(channel.members))
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["category"], value=channel.category)
        embed.add_field(name=getlang(lang)["general"]["channelinfo"]["created_at"], value=channel.created_at.strftime("%d %b %Y %H:%M"))

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def urban(self, ctx, *, search_terms: str, definition_number: int = 1):
        """Search Urban Dictionary"""

        if not ctx.channel.is_nsfw():
            return await ctx.send("Please use this in an NSFW channel.", delete_after=5)

        def encode(s):
            return quote_plus(s, encoding='utf-8', errors='replace')

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
                msg = pagify(msg, ["\n"])
                for page in msg:
                    await ctx.send(page)
            else:
                await ctx.send("Your search terms gave no results.")
        except IndexError:
            await ctx.send("There is no definition #{}".format(pos + 1))
        except Exception as e:
            await ctx.send(f"Error. {e}")

    @commands.command(hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dominant(self, ctx):
        """Get dominant color from image"""
        if not len(ctx.message.attachments) >= 1:
            return await ctx.send("No images given")

        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as cs:
            async with cs.get(ctx.message.attachments[0].url) as r:
                res = await r.read()

        color_thief = ColorThief(BytesIO(res))
        rgb = color_thief.get_color()
        hexx = int(triplet(rgb), 16)

        em = discord.Embed(color=hexx)
        em.title = "Most Dominant Colors"
        em.add_field(name="Int", value=str(hexx))
        em.add_field(name="RGB", value="R %s G %s B %s" % (rgb[0], rgb[1], rgb[2]))
        em.add_field(name="Hex", value="0x"+str(triplet(rgb)).upper())
        em.set_image(url=ctx.message.attachments[0].url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx, user: discord.Member = None, type:str = None):
        """Get a user's avatar"""
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.message.author
        async with aiohttp.ClientSession() as cs:
            async with cs.get(user.avatar_url_as(format='png')) as r:
                res = await r.read()
        color_thief = ColorThief(BytesIO(res))
        hexx = int(triplet(color_thief.get_color()), 16)
        em = discord.Embed(color=hexx, title=f"{user.name}'s Avatar")
        if type is None or type not in ['jpeg', 'jpg', 'png']:
            await ctx.send(embed=em.set_image(url=user.avatar_url))
        else:
            await ctx.send(embed=em.set_image(url=user.avatar_url_as(format=type)))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def coffee(self, ctx):
        """Coffee owo"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        url = "https://coffee.alexflipnote.xyz/random.json"
        await ctx.channel.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
            em = discord.Embed()
            msg = await ctx.send(getlang(lang)["general"]["coffee"], embed=em.set_image(url=res['file']))
            async with cs.get(res['file']) as r:
                data = await r.read()
            color_thief = ColorThief(BytesIO(data))
            hexx = int(triplet(color_thief.get_color()), 16)
            em = discord.Embed(color=hexx)
            await msg.edit(embed=em.set_image(url=res['file']))

    # @commands.command()
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def animepic(self, ctx):
    #     url = "https://api.computerfreaker.cf/v1/anime"
    #     await ctx.channel.trigger_typing()
    #     async with aiohttp.ClientSession() as cs:
    #         async with cs.get(url) as r:
    #             res = await r.json()
    #         em = discord.Embed()
    #         msg = await ctx.send(embed=em.set_image(url=res['url']))
    #         async with cs.get(res['url']) as r:
    #             data = await r.read()
    #         color_thief = ColorThief(BytesIO(data))
    #         hexx = int(triplet(color_thief.get_color()), 16)
    #         em = discord.Embed(color=hexx)
    #         await msg.edit(embed=em.set_image(url=res['url']))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def qr(self, ctx, *, message: str):
        """Generate a QR Code"""
        name = str(uuid.uuid4())
        qrcode.make(message).save(f"{name}.png")
        await ctx.send(file=discord.File(f"{name}.png"))
        os.remove(f"{name}.png")

    @commands.command()
    async def vote(self, ctx):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        embed = discord.Embed(color=0xDEADBF,
                              title=getlang(lang)["general"]["voting_link"],
                              description="https://discordbots.org/bot/310039170792030211/vote")
        await ctx.send(embed=embed)

    @commands.command(aliases=["perms"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def permissions(self, ctx, user: discord.Member = None, channel: str = None):
        """Get Permissions,

        Example Usage:
            n!permissions/n!perms @ReKT#0001 testing
        or
            n!permissions/n!perms ReKT#0001 #testing"""
        if user == None:
            user = ctx.message.author

        if channel == None:
            channel = ctx.message.channel
        else:
            channel = discord.utils.get(ctx.message.guild.channels, name=channel)
        try:
            perms = user.permissions_in(channel)
            if perms.create_instant_invite:
                create_instant_invite = "✅"
            else:
                create_instant_invite = "❌"
            if perms.kick_members:
                kick_members = "✅"
            else:
                kick_members = "❌"
            if perms.ban_members:
                ban_members = "✅"
            else:
                ban_members = "❌"
            if perms.administrator:
                administrator = "✅"
            else:
                administrator = "❌"
            if perms.manage_channels:
                manage_channels = "✅"
            else:
                manage_channels = "❌"
            if perms.manage_guild:
                manage_guild = "✅"
            else:
                manage_guild = "❌"
            if perms.add_reactions:
                add_reactions = "✅"
            else:
                add_reactions = "❌"
            if perms.view_audit_log:
                view_audit_log = "✅"
            else:
                view_audit_log = "❌"
            if perms.read_messages:
                read_messages = "✅"
            else:
                read_messages = "❌"
            if perms.send_messages:
                send_messages = "✅"
            else:
                send_messages = "❌"
            if perms.send_tts_messages:
                send_tts_messages = "✅"
            else:
                send_tts_messages = "❌"
            if perms.manage_messages:
                manage_messages = "✅"
            else:
                manage_messages = "❌"
            if perms.embed_links:
                embed_links = "✅"
            else:
                embed_links = "❌"
            if perms.attach_files:
                attach_files = "✅"
            else:
                attach_files = "❌"
            if perms.read_message_history:
                read_message_history = "✅"
            else:
                read_message_history = "❌"
            if perms.mention_everyone:
                mention_everyone = "✅"
            else:
                mention_everyone = "❌"
            if perms.external_emojis:
                external_emojis = "✅"
            else:
                external_emojis = "❌"
            if perms.mute_members:
                mute_members = "✅"
            else:
                mute_members = "❌"
            if perms.deafen_members:
                deafen_members = "✅"
            else:
                deafen_members = "❌"
            if perms.move_members:
                move_members = "✅"
            else:
                move_members = "❌"
            if perms.change_nickname:
                change_nickname = "✅"
            else:
                change_nickname = "❌"
            if perms.manage_roles:
                manage_roles = "✅"
            else:
                manage_roles = "❌"
            if perms.manage_webhooks:
                manage_webhooks = "✅"
            else:
                manage_webhooks = "❌"
            if perms.manage_emojis:
                manage_emojis = "✅"
            else:
                manage_emojis = "❌"
            if perms.manage_nicknames:
                manage_nicknames = "✅"
            else:
                manage_nicknames = "❌"

            embed = discord.Embed(color=0xDEADBF,
                                  title=f"Permissions for {user.name} in {channel.name}",
                                  description=f"```css\n"
                                              f"Administrator       {administrator}\n"
                                              f"View Audit Log      {view_audit_log}\n"
                                              f"Manage Server       {manage_guild}\n"
                                              f"Manage Channels     {manage_channels}\n"
                                              f"Kick Members        {kick_members}\n"
                                              f"Ban Members         {ban_members}\n"
                                              f"Create Invite       {create_instant_invite}\n"
                                              f"Change Nickname     {change_nickname}\n"
                                              f"Manage Nicknames    {manage_nicknames}\n"
                                              f"Manage Emojis       {manage_emojis}\n"
                                              f"Read Messages       {read_messages}\n"
                                              f"Read History        {read_message_history}\n"
                                              f"Send Messages       {send_messages}\n"
                                              f"Send TTS Messages   {send_tts_messages}\n"
                                              f"Manage Messages     {manage_messages}\n"
                                              f"Embed Links         {embed_links}\n"
                                              f"Attach Files        {attach_files}\n"
                                              f"Mention Everyone    {mention_everyone}\n"
                                              f"Use External Emotes {external_emojis}\n"
                                              f"Add Reactions       {add_reactions}\n"
                                              f"Manage Webhooks     {manage_webhooks}\n"
                                              f"Manage Roles        {manage_roles}\n"
                                              f"Mute Members        {mute_members}\n"
                                              f"Deafen Members      {deafen_members}\n"
                                              f"Move Members        {move_members}"
                                              f"```")
            if ctx.message.guild.owner_id == user.id:
                embed.set_footer(text="Is Owner.")
            await ctx.send(embed=embed)
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
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def botinfo(self, ctx, bot_user : discord.Member = None):
        """Get Bot Info"""
        if bot_user == None:
            bot_user = self.bot.user
        await ctx.trigger_typing()
        url = f"https://discordbots.org/api/bots/{bot_user.id}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                bot = await r.json()
        try:
            em = discord.Embed(color=0xDEADBF, title=bot['username'] + "#" + bot['discriminator'],
                               description=bot['shortdesc'])
            try:
                em.add_field(name="Prefix", value=bot['prefix'])
            except:
                pass
            try:
                em.add_field(name="Lib", value=bot['lib'])
            except:
                pass
            try:
                em.add_field(name="Owners", value=f"<@{bot['owners'][0]}>")
            except:
                pass
            try:
                em.add_field(name="Votes", value=bot['points'])
            except:
                pass
            try:
                em.add_field(name="Server Count", value=bot['server_count'])
            except:
                pass
            try:
                em.add_field(name="ID", value=bot['id'])
            except:
                pass
            try:
                em.add_field(name="Certified", value=bot['certifiedBot'])
            except:
                pass
            try:
                em.add_field(name="Links", value=f"[GitHub]({bot['github']}) - [Invite]({bot['invite']})")
            except:
                pass
            try:
                em.set_thumbnail(url=f"https://images.discordapp.net/avatars/{bot['id']}/{bot['avatar']}")
            except:
                pass
        except:
            return await ctx.send("Failed to get bot data.")

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def discriminfo(self, ctx):
        """Get some stats about the servers discrims"""
        discrim_list = [int(u.discriminator) for u in ctx.guild.members]

        # The range is so we can get any discrims that no one has.
        # Just subtract one from the number of uses.
        count = Counter(discrim_list + [int(i) for i in range(1, 10000)])
        count = sorted(count.items(), key=lambda c: c[1], reverse=True)

        embeds = {
            'Summary': {
                'Most Common': ', '.join(str(d[0]) for d in count[:3])
                               + ', and ' + str(count[4][0]),
                'Least Common': ', '.join(str(d[0]) for d in count[-4:-1][::-1])
                                + ', and ' + str(count[-1][0]),
                'Three Unused': '\n'.join([str(d[0]) for d in count
                                           if d[1] == 1][:3]),
                'Average': numpy.mean(discrim_list),
            },
            'Statistics': {
                'Average': numpy.mean(discrim_list),
                'Mode': stats.mode(discrim_list)[0][0],
                'Median': numpy.median(discrim_list),
                'Standard Deviation': numpy.std(discrim_list),
            }
        }

        final_embeds = []

        for embed_title in embeds.keys():
            e = discord.Embed(title=embed_title)
            for field_name in embeds[embed_title].keys():
                e.add_field(name=field_name,
                            value=embeds[embed_title][field_name], inline=False)
            final_embeds.append(e)

        p = EmbedPages(ctx, embeds=final_embeds)
        await p.paginate()

    # It's a converter, not a type annotation in this case
    # noinspection PyTypeChecker
    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def discrim(self, ctx, discriminator: Discriminator = None,
                      *, selector: Selector = '='):
        """Search for specific discriminators.

        Optional parameter for ranges to be searched.

        It can be >, >=, <=, or <.

        Ranges between two numbers hasn't been implemented yet."""
        if not discriminator:
            discriminator = int(ctx.author.discriminator)
        if selector == '>':
            p = Pages(ctx, entries=[
                f'{u.display_name}#{u.discriminator}'
                for u in ctx.guild.members
                if int(u.discriminator) > discriminator
            ])
        elif selector == '<':
            p = Pages(ctx, entries=[
                f'{u.display_name}#{u.discriminator}'
                for u in ctx.guild.members
                if int(u.discriminator) < discriminator
            ])
        elif selector == '>=':
            p = Pages(ctx, entries=[
                f'{u.display_name}#{u.discriminator}'
                for u in ctx.guild.members
                if int(u.discriminator) >= discriminator
            ])
        elif selector == '<=':
            p = Pages(ctx, entries=[
                f'{u.display_name}#{u.discriminator}'
                for u in ctx.guild.members
                if int(u.discriminator) <= discriminator
            ])
        elif selector == '=':
            p = Pages(ctx, entries=[
                f'{u.display_name}#{u.discriminator}'
                for u in ctx.guild.members
                if int(u.discriminator) == discriminator
            ])
        else:
            raise commands.BadArgument('Could not parse arguments')

        if not p.entries:
            return await ctx.send('No results found.')

        await p.paginate()

    @commands.group(hidden=True)
    @commands.is_owner()
    async def config(self, ctx):
        """Configuration"""
        if ctx.invoked_subcommand is None:
            em = discord.Embed(color=0xDEADBF, title="Config",
                               description=" - avatar, **Owner Only**\n"
                                           "- username, **Owner Only**\n"
                                           "- blacklist, **Owner Only**\n"
                                           "- reset, **Owner Only**\n"
                                           "- freeze, **Owner Only**")
            await ctx.send(embed=em)

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
    async def conf_reset(self, ctx, userid:int):
        """Reset user"""
        await r.table("levelSystem").get(str(userid)).update({"xp": 0, "lastxptimes": [], "lastxp": "0"}).run(self.bot.r_conn)
        await ctx.send("Reset user.")

    @config.command(hidden=True, name="freeze")
    @commands.is_owner()
    async def conf_freeze(self, ctx, userid:int):
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
    async def addvote(self, ctx, *user_ids:int):
        """Add user id to votes"""
        try:
            users_added = []
            for userid in user_ids:
                await r.table("votes").insert({"id": str(userid)}).run(self.bot.r_conn)
                users_added.append(userid)
            await ctx.send("Added %s users to the db" % (len(users_added),))
        except Exception as e:
            await ctx.send(f"`{e}`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def getuser(self, ctx, userid:int):
        """Get user from id"""
        try:
            user = await self.bot.get_user_info(userid)
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
                em.add_field(name="Level", value=str(int((1 / 278) * (9 + math.sqrt(81 + 1112 * (level["xp"]))))))
                em.add_field(name="Blacklisted?", value=str(level["blacklisted"]))
                em.add_field(name="Last XP", value=level["lastxp"])
            await ctx.send(embed=em)
        except:
            await ctx.send("Failed to find user.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shorten(self, ctx, *, url:str):
        """Shorten a URL"""
        url = f"https://api-ssl.bitly.com/v3/shorten?access_token={config.bitly}&longUrl={url}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        if res["status_code"] != 200:
            em = discord.Embed(color=0xDEADBF, title="Error",
                               description=f"Error: {res['status_txt']}\nMake sure the URL starts with http(s)://")
            return await ctx.send(embed=em)
        em = discord.Embed(color=0xDEADBF, title="Shortened URL", description=res["data"]["url"])
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        """Get the bots invite"""
        await ctx.send("**Invite the bot:** <https://uwu.whats-th.is/32dde7>\n"
                       "**Support Server:** <https://discord.gg/q98qeYN>")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def system(self, ctx):
        """Get Bot System Info"""
        try:
            cpu_per = psutil.cpu_percent()
            cores = psutil.cpu_count()
            memory = psutil.virtual_memory().total >> 20
            mem_usage = psutil.virtual_memory().used >> 20
            storage_free = psutil.disk_usage('/').free >> 30
            em = discord.Embed(color=0xDEADBF, title="System Stats",
                               description=f"Cores: **{cores}**\n"
                                           f"CPU%: **{cpu_per}**\n"
                                           f"RAM Usage: **{mem_usage}/{memory} MB** ({int(memory - mem_usage)}MB free)\n"
                                           f"Storage: **{storage_free} Free GB**")
            await ctx.send(embed=em)
        except Exception as e:
            await ctx.send(f"Failed to get system info,\nError: {e}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def prefix(self, ctx):
        """Get the bots current prefix."""
        currprefix = await self.bot.redis.get(f"{ctx.author.id}-prefix")
        if currprefix:
            currprefix = currprefix.decode("utf8")
            await ctx.send(f"Your custom prefix is set to `{currprefix}`")
        else:
            await ctx.send("My prefix is `n!` or `N!`")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def setprefix(self, ctx, prefix:str):
        """Set your custom prefix, use quotation marks like "baka " for spaces."""
        if len(prefix) >= 12:
            return await ctx.send("Your prefix is over 12 characters.")
        await self.bot.redis.set(f"{ctx.author.id}-prefix", prefix)
        await ctx.send(f"Set **your** custom prefix to `{prefix}`, you can remove it by pinging me and using delprefix.")

    @commands.command(aliases=["deleteprefix", "resetprefix"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def delprefix(self, ctx):
        """Delete or reset your prefix"""
        await self.bot.redis.delete(f"{ctx.author.id}-prefix")
        await ctx.send("Deleted your prefix and reset it back to the default `n!`")

    @commands.command()
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def help(self, ctx, command:str=None):
        """Help!"""
        if command:
            entity = self.bot.get_cog(command) or self.bot.get_command(command)

            if entity:
                if isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)
                return await p.paginate()
        try:
            other = ""
            other += "`pet`, "
            other += "`card`, "
            other += "`imgwelcome`, "
            other += ", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "Marriage"])
            embed = discord.Embed(color=0xDEADBF, title="NekoBot Help")
            try:
                embed.add_field(name="Donator",
                                value=", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "Donator" and not i.hidden]),
                                inline=False)
            except: pass
            try:
                embed.add_field(name="Economy",
                                value=", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "economy" and not i.hidden]),
                                inline=False)
            except: pass
            try:
                embed.add_field(name="Fun",
                                value=", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "Fun" and not i.hidden]),
                                inline=False)
            except: pass
            try:
                embed.add_field(name="Games",
                                value=", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "Games" and not i.hidden]),
                                inline=False)
            except: pass
            try:
                embed.add_field(name="General",
                                value=", ".join(
                                    [f"`{i.name}`" for i in self.bot.commands if i.cog_name == "General" and not i.hidden]),
                                inline=False)
            except: pass
            try:
                embed.add_field(name="Moderation",
                                value=", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "Moderation" and not i.hidden]),
                                inline=False)
            except: pass
            try:
                embed.add_field(name="NSFW",
                                value=", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "NSFW" and not i.hidden]),
                                inline=False)
            except: pass
            try:
                embed.add_field(name="Reactions",
                                value=", ".join([f"`{i.name}`" for i in self.bot.commands if i.cog_name == "Reactions" and not i.hidden]),
                                inline=False)
            except: pass
            embed.add_field(name="Other", value=other, inline=False)
            await ctx.send(embed=embed)
        except discord.HTTPException:
            return await ctx.send("**I can't send embeds.**")
        except:
            pass
        try:
            emoji = self.bot.get_emoji(408672929379909632)
            await ctx.message.add_reaction(emoji)
        except:
            pass

def setup(bot):
    if not hasattr(bot, 'socket_stats'):
        bot.socket_stats = Counter()
    bot.remove_command('help')
    bot.add_cog(General(bot))
