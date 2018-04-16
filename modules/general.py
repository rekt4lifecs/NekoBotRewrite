from discord.ext import commands
import discord
import datetime, random, config, math, aiohttp, aiomysql
from collections import Counter
from hurry.filesize import size
from .utils.chat_formatting import pagify
from PIL import __version__ as pilv
from bs4 import __version__ as bsv
from urllib.parse import quote_plus
import string, json
from .utils.paginator import EmbedPages, Pages
from scipy import stats
import numpy
from .utils.paginator import HelpPaginator

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

class General:
    """General Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()

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

    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms: str):
        """Creates a lmgtfy link"""
        search_terms = search_terms.replace(" ", "+")
        await ctx.send("https://lmgtfy.com/?q={}".format(search_terms))

    @commands.command(pass_context=True)
    async def cookie(self, ctx, user: discord.Member):
        """Give somebody a cookie :3"""
        await ctx.send(
            "<:NekoCookie:408672929379909632> - **{} gave {} a cookie OwO** - <:NekoCookie:408672929379909632>".format(
                ctx.message.author.name, user.mention))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def flip(self, ctx):
        """Flip a coin"""
        x = random.randint(0, 1)
        if x == 1:
            await ctx.send("**Heads**", file=discord.File("data/heads.png"))
        else:
            await ctx.send("**Tails**", file=discord.File("data/tails.png"))

    def id_generator(self, size=7, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @commands.command(aliases=['version'])
    async def info(self, ctx):
        servers = len(self.bot.guilds)
        info = discord.Embed(title="**Info**",
                             color=0xDEADBF,
                             description=f"Servers: **{millify(servers)} ({servers})**\n"
                                         f"Members **{millify(len(set(self.bot.get_all_members())))}**\n"
                                         f"Bot Commands: **{str(len(self.bot.commands))}**\n"
                                         f"Channels: **{millify(len(set(self.bot.get_all_channels())))}**\n"
                                         f"Shards: **{self.bot.shard_count}**\n"
                                         f"Bot in voice channel(s): **{len(self.bot.voice_clients)}**\n"
                                         f"Messages Read (Since Restart): **{millify(self.bot.counter['messages_read'])}**")
        # try:
        #     info.add_field(name="System:", value=f"CPU %: **{psutil.cpu_percent()}%**\n"
        #                                      f"Boot Time: **{datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}**\n"
        #                                      f"**Discord.py** {discord.__version__} | **PIL** {pilv} | **BeautifulSoup** {bsv} | **psutil** {psutil.__version__} | **aiomysql** {aiomysql.__version__} | **aiohttp** {aiohttp.__version__}")
        # except:
        #     pass
        # try:
        #     info.add_field(name="System", value=f"discord.py {discord.__version__} | BeautifulSoup {bsv} | Pillow {pilv} | ")
        # except:
        #     pass
        info.add_field(name="Links", value="<:GH:416593854368841729> - [GitHub](https://github.com/rekt4lifecs/NekoBotRewrite/) |"
                                           " [Support Server](https://discord.gg/q98qeYN) | "
                                           "[Vote OwO](https://discordbots.org/bot/310039170792030211/vote) | <:nkotreon:430733839003025409> [Patreon](https://www.patreon.com/NekoBot)")
        info.set_footer(
            text="Bot by ReKT#0001 & Kot#0001 :^)")
        info.set_thumbnail(url=self.bot.user.avatar_url_as(format='png'))
        await ctx.send(embed=info)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def whois(self, ctx, userid:int):
        """Lookup a user with a userid"""
        user = self.bot.get_user(userid)
        if user is None:
            return await ctx.send(f"```css\n[ Whois Lookup for {userid} ]\n\nUser not found!```")
        text = f"```css\n" \
               f"[ Whois Lookup for {userid} ]\n\n" \
               f"Name:      {user.name}\n" \
               f"ID:        {user.id}\n" \
               f"Discrim:   {user.discriminator}\n" \
               f"Bot:       {user.bot}\n" \
               f"Created:   {user.created_at}\n" \
               f"```"
        embed = discord.Embed(color=0xDEADBF, description=text)
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['user'])
    @commands.guild_only()
    async def userinfo(self, ctx, user: discord.Member = None):
        """Get a users info."""
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
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Discriminator", value=user.discriminator)
        embed.add_field(name="Bot", value=str(user.bot))
        embed.add_field(name="Created", value=user.created_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name="Joined", value=user.joined_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name="Animated Avatar", value=str(user.is_avatar_animated()))
        embed.add_field(name="Playing", value=playinggame)
        embed.add_field(name="Status", value=user.status)
        embed.add_field(name="Color", value=user.color)

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
        server = ctx.message.guild

        verif = server.verification_level

        online = len([m.status for m in server.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])

        embed = discord.Embed(color=0xDEADBF)
        embed.add_field(name="Name", value=f"**{server.name}**\n({server.id})")
        embed.add_field(name="Owner", value=server.owner)
        embed.add_field(name="Online", value=f"**{online}/{len(server.members)}**")
        embed.add_field(name="Created at", value=server.created_at.strftime("%d %b %Y %H:%M"))
        embed.add_field(name="Channels", value=f"Text Channels: **{len(server.text_channels)}**\n"
                                               f"Voice Channels: **{len(server.voice_channels)}**\n"
                                               f"Categories: **{len(server.categories)}**\n"
                                               f"AFK Channel: **{server.afk_channel}**")
        embed.add_field(name="Roles", value=len(server.roles))
        embed.add_field(name="Emojis", value=f"{len(server.emojis)}/100")
        embed.add_field(name="Region", value=str(server.region).title())
        embed.add_field(name="Security", value=f"Verification Level: **{verif}**\n"
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
        if channel is None:
            channel = ctx.message.channel

        embed = discord.Embed(color=0xDEADBF,
                              description=channel.mention)
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="Guild", value=channel.guild)
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="Category ID", value=channel.category_id)
        embed.add_field(name="Position", value=channel.position)
        embed.add_field(name="NSFW", value=str(channel.is_nsfw()))
        embed.add_field(name="Members", value=len(channel.members))
        embed.add_field(name="Category", value=channel.category)
        embed.add_field(name="Created at", value=channel.created_at.strftime("%d %b %Y %H:%M"))

        await ctx.send(embed=embed)

    @commands.command()
    async def urban(self, ctx, *, search_terms: str, definition_number: int = 1):
        """Search Urban Dictionary"""

        def encode(s):
            return quote_plus(s, encoding='utf-8', errors='replace')

        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11):  # API only provides the
                pos = 0                  # top 10 definitions
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

    @commands.command()
    async def verify(self, ctx, user : discord.Member = None):
        """Verify Server."""
        server = ctx.message.guild
        if server.id == 310037773786677258:
            if user is None:
                user = ctx.message.author
            try:
                emoji = self.bot.get_emoji(408672929379909632)
                await ctx.message.add_reaction(emoji)
            except:
                pass
            await user.send(f"Verification link: https://captcha.nayami.party/?sid={server.id}&u={user.id}")
        else:
            return

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """Get a user's avatar"""
        if user == None:
            user = ctx.message.author
        await ctx.send(user.avatar_url_as(format="png"))

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def qr(self, ctx, *, message: str):
        """Generate a QR Code"""
        new_message = message.replace(" ", "+")
        url = f"http://api.qrserver.com/v1/create-qr-code/?data={new_message}"

        embed = discord.Embed(color=0xDEADBF)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command()
    async def docs(self, ctx):
        """Full docs MonkaS"""
        await ctx.send("https://rekt4lifecs.github.io/NekoBotRewrite/")

    @commands.command()
    async def vote(self, ctx):
        embed = discord.Embed(color=0xDEADBF,
                              title="Voting Link",
                              description="https://discordbots.org/bot/310039170792030211/vote")
        await ctx.send(embed=embed)

    @commands.command(aliases=["perms"])
    async def permissions(self, ctx, user: discord.Member = None, channel: str = None):
        """Get Permissions,

        Example Usage:
            .permissions/.perms @ReKT#0001 testing
        or
            .permissions/.perms ReKT#0001 #testing
        anyway doesn't matter ;p"""
        if user == None:
            user = ctx.message.author

        if channel == None:
            channel = ctx.message.channel
        else:
            channel = discord.utils.get(ctx.message.guild.channels, name=channel)
            print(channel)
        amount = await self.execute(isSelect=True, query=f"SELECT 1 FROM dbl WHERE user = {ctx.message.author.id} AND type = \"upvote\"")
        if amount != 0:
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
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="OwO Whats this",
                                  description="To use this command you need to `n!vote` >.<")
            await ctx.send(embed=embed)

    @commands.command(aliases=["8"], name="8ball")
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

    @commands.command(aliases=['ddg'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def duckduckgo(self, ctx, *, search_terms: str):
        search = search_terms.replace(" ", "%20")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"http://api.duckduckgo.com/?q={search}&format=json") as r:
                res = await r.read()
                res = json.loads(res)
                try:
                    data = res['RelatedTopics'][0]['Text']
                    url = res['RelatedTopics'][0]['FirstURL']
                except:
                    return await ctx.send("**No search results found.**")
                embed = discord.Embed(color=0xDEADBF, title=f"Search results for {search_terms}",
                                      description=f"[{data}]({url})")
                await ctx.send(embed=embed)

    @commands.command()
    async def botinfo(self, ctx, bot_user : int = None):
        """Get Bot Info"""
        if bot_user == None:
            bot_user = self.bot.user.id
        url = f"https://discordbots.org/api/bots/{bot_user}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                bot = await r.json()

        em = discord.Embed(color=0xDEADBF, title=bot['username'] + "#" + bot['discriminator'], description=bot['shortdesc'])
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

        await ctx.send(embed=em)

    @commands.command()
    async def calc(self, ctx, num1 : int, operator : str, num2 : int):
        """Calculator, +, -, *, /"""
        try:
            if operator == "+":
                i = num1 + num2
            elif operator == "-":
                i = num1 - num2
            elif operator == "*":
                i = num1 * num2
            elif operator == '/':
                i = num1 / num2
            else:
                await ctx.send("Not a valid operator.")
                return
            await ctx.send(i)
        except Exception as e:
            await ctx.send(embed=discord.Embed(color=0xDEADBF, title="⛔ Error", description=f"```\n"
                                                                                      f"{e}\n"
                                                                                      f"```"))

    @commands.command()
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

    @commands.command()
    async def help(self, ctx, option: str = None):
        """Help Command OwO"""
        color = 0xDEADBF
        if not option is None:
            entity = self.bot.get_cog(option) or self.bot.get_command(option)

            if entity is None:
                clean = option.replace('@', '@\u200b')
                return await ctx.send(f'Command or category "{clean}" not found.')
            elif isinstance(entity, commands.Command):
                p = await HelpPaginator.from_command(ctx, entity)
            else:
                p = await HelpPaginator.from_cog(ctx, entity)
            return await p.paginate()
        try:
            latency = "%.4f" % self.bot.latencies[0][1]
            embed = discord.Embed(color=color,
                                  title=f"Prefix: When Mentioned or 'n!'",
                                  description=f"Latency: {latency}")
            embed.set_author(name="NekoBot",
                             icon_url="https://i.imgur.com/x2N73t0.png")

            embed.add_field(name="General",
                            value="`lmgtfy`, `cookie`, `flip`, `info`, `userinfo`, `serverinfo`, `channelinfo`, `urban`,"
                                  " `avatar`, `qr`, `docs`, `vote`, `permissions`, `8ball`, `help`, `calc`, `crypto`, `duckduckgo`, `whois`, `memory`, "
                                  "`discriminfo`, `discrim`", inline=False)
            embed.add_field(name="Audio", value="`play`, `skip`, `stop`, `now`, `queue`, `pause`, `volume`, `shuffle`, `repeat`, `find`, `disconnect`", inline=True)
            embed.add_field(name="Donator", value="`donate`, `redeem`, `upload`, `trapcard`")
            embed.add_field(name="Moderation",
                            value="`kick`, `ban`, `massban`, `unban`, `rename`, `poll`, `purge`, `mute`, `unmute`, `dehoist`", inline=False)
            embed.add_field(name="Roleplay", value="`card`")
            embed.add_field(name="IMGWelcomer", value="`imgwelcome`", inline=False)
            embed.add_field(name="Levels & Economy", value="`bank`, `register`, `profile`, `daily`, `rep`, `setdesc`, `transfer`, "
                                                           "`coinflip`, `blackjack`", inline=False)
            embed.add_field(name="Fun",
                            value="`food`, `toxicity`, `ship`, `achievement`, `shitpost`, `meme`, `changemymind`, `penis`, `vagina`, `jpeg`, `isnowillegal`, `gif`, `cat`, `dog`, "
                                  "`bitconnect`, `feed`, `lovecalculator`, `butts`, `boom`, `rude`, `fight`, `clyde`, `monkaS`, `joke`, "
                                  "`b64`, `md5`, `kannagen`, `iphonex`, `baguette`, `owoify`, `lizard`, `duck`, `captcha`, `whowouldwin`", inline=False)

            embed.add_field(name="NSFW",
                            value="`pgif`, `4k`, `phsearch`, `yandere`, `boobs`, `bigboobs`, `ass`, `cumsluts`, `thighs`,"
                                  " `gonewild`, `nsfw`, `doujin`, `girl`, `hentai`, `rule34`", inline=False)

            embed.add_field(name="Reactions",
                            value="`awoo`, `blush`, `confused`, `cry`, `dance`, `insult`, `cry`, `hug`, `kiss`, `pat`, `cuddle`, `tickle`, `bite`, `slap`, `punch`,"
                                  "`poke`, `nom`, `lick`, `lewd`, `trap`, `owo`, `wasted`, `banghead`,"
                                  "`discordmeme`, `stare`, `thinking`, `dab`, `kemonomimi`, `why`, `rem`, `poi`, `greet`, "
                                  "`insultwaifu`, `foxgirl`, `jojo`, `megumin`, `pout`, `shrug`, `sleepy`, `sumfuk`, `initiald`, `deredere`", inline=False)
            embed.add_field(name="Game Stats",
                            value="`osu`, `overwatch`, `fortnite`, `minecraft`", inline=False)
            embed.add_field(name="Marriage", value="`marry`, `divorce`", inline=False)

            await ctx.send(embed=embed)
        except:
            await ctx.send("I can't send embeds.")
        try:
            emoji = self.bot.get_emoji(408672929379909632)
            await ctx.message.add_reaction(emoji)
        except:
            pass

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def crypto(self, ctx, crypto: str):
        """Get cryptocurrency info"""
        coin = "USD,EUR,GBP,JPY,CHF,AUD,CAD,INR,IDR,NZD,ZAR,SEK,SGD,KRW,NOK,MXN,BRL,HKD,RUB,MYR,THB,"
        tsyms = coin + "BTC,BCH,ETH,ETC,LTC,XMR,DASH,ZEC,DOGE,DCR"
        url = f"https://min-api.cryptocompare.com/data/price?fsym={crypto.upper()}&tsyms={tsyms}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        try:
            USD  = res['USD']
            EUR  = res['EUR']
            GBP  = res['GBP']
            JPY  = res['JPY']
            CHF  = res['CHF']
            AUD  = res['AUD']
            CAD  = res['CAD']
            INR  = res['INR']
            IDR  = res['IDR']
            NZD  = res['NZD']
            ZAR  = res['ZAR']
            SEK  = res['SEK']
            SGD  = res['SGD']
            KRW  = res['KRW']
            NOK  = res['NOK']
            MXN  = res['MXN']
            BRL  = res['BRL']
            HKD  = res['HKD']
            RUB  = res['RUB']
            MYR  = res['MYR']
            THB  = res['THB']

            BTC  = res['BTC']
            BCH  = res['BCH']
            ETH  = res['ETH']
            LTC  = res['LTC']
            XMR  = res['XMR']
            DASH = res['DASH']
            ZEC  = res['ZEC']
            DOGE = res['DOGE']
            DCR  = res['DCR']

            e = discord.Embed(color=0xDEADBF, title=f"{crypto.upper()} Conversion",
                              description=f"🇺🇸 US Dollar: **${USD}**\n"
                                          f"🇪🇺 Euro: **€{EUR}**\n"
                                          f"🇬🇧 British Pound: **£{GBP}**\n"
                                          f"🇯🇵 Japanese Yen: **¥{JPY}**\n"
                                          f"🇨🇭 Swiss Franc: **Fr.{CHF}**\n"
                                          f"🇦🇺 Australian Dollar: **${AUD}**\n"
                                          f"🇨🇦 Canadian Dollar: **${CAD}**\n"
                                          f"🇮🇳 Indian Rupee: **₹{INR}**\n"
                                          f"🇮🇩 Indonesian Rupiah: **IDR {IDR}**\n"
                                          f"🇳🇿 New Zealand Dollar: **${NZD}**\n"
                                          f"🇿🇦 South African Rand: **R{ZAR}**\n"
                                          f"🇸🇪 Swedish Krona: **kr {SEK}**\n"
                                          f"🇸🇬 Singapore Dollar: **${SGD}**\n"
                                          f"🇰🇷 South Korean Won: **₩{KRW}**\n"
                                          f"🇳🇴 Norwegian Krone: **kr {NOK}**\n"
                                          f"🇲🇽 Mexican Peso: **Mex${MXN}**\n"
                                          f"🇧🇷 Brazilian Real: **R${BRL}**\n"
                                          f"🇭🇰 Hong Kong Dollar: **HK${HKD}**\n"
                                          f"🇷🇺 Russian Ruble: **₽{RUB}**\n"
                                          f"🇲🇾 Malaysian Ringgit: **RM {MYR}**\n"
                                          f"🇹🇭 Thai Baht: **฿ {THB}**")
            e.add_field(name="Cryptocurrency",
                        value=f"<:bitcoin:423859742281302036> Bitcoin: **₿{BTC}**\n"
                              f"<:bitcoincash:423863215840034817> Bitcoin Cash: {BCH}**\n"
                              f"<:eth:423859767211982858> Ethereum: ♦{ETH}**\n"
                              f"<:ltc:423859753698197507> Litecoin: Ł{LTC}**\n"
                              f"<:monero:423859744936034314> Monero: ɱ{XMR}**\n"
                              f"<:dash:423859742520377346> Dash: {DASH}**\n"
                              f"<:yellowzcashlogo:423859752045379594> Zcash: ⓩ{ZEC}**\n"
                              f"<:dogecoin:423859755384045569> Dogecoin: Đ{DOGE}**\n"
                              f"<:decred:423859744361676801> Decred: {DCR}**", inline=True)
        except:
            e = discord.Embed(color=0xDEADBF, title="⚠ Error", description="Not a valid currency format.")
        await ctx.send(embed=e)

    # @commands.command()
    # async def help(self, ctx, *, command: str = None):
    #     """Show's help"""
    #     try:
    #         if command is None:
    #             p = await HelpPaginator.from_bot(ctx)
    #         else:
    #             entity = self.bot.get_cog(command) or self.bot.get_command(command)
    #
    #             if entity is None:
    #                 clean = command.replace('@', '@\u200b')
    #                 return await ctx.send(f'Command or category "{clean}" not found.')
    #             elif isinstance(entity, commands.Command):
    #                 p = await HelpPaginator.from_command(ctx, entity)
    #             else:
    #                 p = await HelpPaginator.from_cog(ctx, entity)
    #
    #         await p.paginate()
    #     except Exception as e:
    #         return await ctx.send(chat_formatting.bold(e))


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(General(bot))
