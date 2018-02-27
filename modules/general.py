from discord.ext import commands
import discord
import sys, psutil, datetime, aiohttp, random, requests, config
from collections import Counter
from hurry.filesize import size
from .utils.chat_formatting import pagify
from PIL import __version__ as pilv
from bs4 import __version__ as bsv
from urllib.parse import quote_plus


class General:
    """General Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()

    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms : str):
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

    @commands.command()
    async def info(self, ctx):
        servers = len(self.bot.guilds)
        info = discord.Embed(title="**Info**",
                             color=0xDEADBF,
                             description=f"Servers: {servers}\n"
                                         f"Members {len(set(self.bot.get_all_members()))}\n"
                                         f"Bot Commands: {str(len(self.bot.commands))}\n"
                                         f"Channels: {len(set(self.bot.get_all_channels()))}\n"
                                         f"Shards: {self.bot.shard_count}")
        info.add_field(name="Messages Read", value=self.bot.counter['messages_read'])
        info.add_field(name="Processed Commands", value=self.bot.counter['commands'])
        info.add_field(name="CPU %", value=psutil.cpu_percent())
        info.add_field(name="Virtual Memory", value=f"{size(psutil.virtual_memory().available)}")
        info.add_field(name="Disk",
                       value=f"Free Space {size(psutil.disk_usage(psutil.disk_partitions()[0].device).free)}")
        info.add_field(name="Boot Time",
                       value=datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'))
        info.add_field(name=f"Python {sys.version[0]}", value=f"Discord.py {discord.__version__}\n"
                                                              f"PIL {pilv}\n"
                                                              f"BeautifulSoup {bsv}")
        info.add_field(name="Links", value="<:GH:416593854368841729> - https://github.com/rekt4lifecs/NekoBotRewrite/\n"
                                           "**Support Server** - https://discord.gg/q98qeYN\n"
                                           "**Vote** OwO - https://discordbots.org/bot/310039170792030211/vote")
        info.set_footer(text="Bot by ReKT#0001 and was forced to use MySQL by Fox#0001 <3, user \"nsfw\" to see the NSFW usage graph owo")
        info.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=info)

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, user : discord.Member = None):
        """Get a users info."""
        if user == None:
            user = ctx.message.author
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
        embed.add_field(name="Playing", value=user.game)
        embed.add_field(name="Status", value=user.status)
        embed.add_field(name="Color", value=user.color)

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"
        embed.add_field(name="Roles", value=roles)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Display Server Info"""
        server = ctx.message.guild

        if server.mfa_level == 1:
            twofac = True
        else:
            twofac = False

        verif = server.verification_level

        online = len([m.status for m in server.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])

        if server.features == []:
            features = "None"
        else:
            features = str(server.features).replace("[", "").replace("]", "")

        embed = discord.Embed(color=0xDEADBF)
        embed.add_field(name="Name", value=server.name)
        embed.add_field(name="Roles", value=len(server.roles))
        embed.add_field(name="Emojis", value=f"{len(server.emojis)}/100")
        embed.add_field(name="Region", value=server.region)
        embed.add_field(name="AFK Timeout", value=server.afk_timeout)
        embed.add_field(name="AFK Channel", value=server.afk_channel)
        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="ID", value=server.id)
        embed.add_field(name="Owner", value=server.owner)
        embed.add_field(name="F2A", value=str(twofac))
        embed.add_field(name="Verification Level", value=verif)
        embed.add_field(name="Online", value=f"{online}/{len(server.members)}")
        embed.add_field(name="Content Filter", value=server.explicit_content_filter)
        embed.add_field(name="Features", value=features)
        embed.add_field(name="Channels", value=len(server.channels))
        embed.add_field(name="Large Guild", value=str(server.large))
        embed.add_field(name="Voice Channels", value=len(server.voice_channels))
        embed.add_field(name="Text Channels", value=len(server.text_channels))
        embed.add_field(name="Categories", value=len(server.categories))
        embed.add_field(name="System Channel", value=server.system_channel)
        embed.add_field(name="Shard ID", value=server.shard_id)
        embed.add_field(name="Created at", value=server.created_at.strftime("%d %b %Y %H:%M"))
        embed.set_footer(text="Thats a lot of info V(=^･ω･^=)v")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def channelinfo(self, ctx, channel : discord.TextChannel = None):
        """Get Channel Info"""
        channel = ctx.message.channel

        embed = discord.Embed(color=0xDEADBF,
                              description=channel.mention)
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="Guild", value=channel.guild)
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="Category ID", value=channel.category_id)
        #embed.add_field(name="Topic", value=channel.topic)
        embed.add_field(name="Position", value=channel.position)
        embed.add_field(name="NSFW", value=str(channel.is_nsfw()))
        embed.add_field(name="Members", value=len(channel.members))
        embed.add_field(name="Category", value=channel.category)
        embed.add_field(name="Created at", value=channel.created_at.strftime("%d %b %Y %H:%M"))

        await ctx.send(embed=embed)


    @commands.command()
    async def urban(self, ctx, *, search_terms : str, definition_number : int=1):
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
            if pos not in range(0, 11): # API only provides the
                pos = 0                 # top 10 definitions
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
                       "**Example:\n**{}".format(pos+1, defs, definition,
                                                 example))
                msg = pagify(msg, ["\n"])
                for page in msg:
                    await ctx.send(page)
            else:
                await ctx.send("Your search terms gave no results.")
        except IndexError:
            await ctx.send("There is no definition #{}".format(pos+1))
        except Exception as e:
            await ctx.send(f"Error. {e}")

    @commands.command()
    async def avatar(self, ctx, user : discord.Member = None):
        """Get a user's avatar"""
        if user == None:
            user = ctx.message.author
        await ctx.send(user.avatar_url_as(format="png"))

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def qr(self, ctx, *, message : str):
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
    async def permissions(self, ctx, user : discord.Member = None, channel : str = None):
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

        url = "https://discordbots.org/api/bots/310039170792030211/votes"
        async with aiohttp.ClientSession(headers={"Authorization": config.dbots.key}) as cs:
            async with cs.get(url) as r:
                res = await r.json()
        for x in res:
            if str(x['id']) == str(ctx.message.author.id):
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
                    break
                except:
                    await ctx.send("Problem getting that channel...")
                    break
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="OwO Whats this",
                                  description="To use this command you need to `.vote` >.<")
            await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx, option : str = None):
        """Help Command OwO"""
        color = 0xDEADBF
        # too lazy to loop kthx fiteme source stealers
        try:
            embed = discord.Embed(color=color)
            embed.set_author(name="NekoBot",
                            icon_url="https://i.imgur.com/x2N73t0.png")

            embed.add_field(name="General",
                            value="`info`, `help`, `perms`, `lmgtfy`, `cookie`, `serverinfo`, `userinfo`, `channelinfo`, `flip`, "
                                 "`avatar`, `urban`, `qr`, `docs` (A full documentation)")
            embed.add_field(name="Moderation", value="`kick`, `ban`, `massban`, `unban`, `rename`, `mute` (VC), `unmute` (VC)")
            embed.add_field(name="IMGWelcomer", value="`imgwelcome`")
            embed.add_field(name="Levels", value="`profile`, `settitle`, `setdesc`, `rep`")
            embed.add_field(name="Fun", value="`ship`, `shitpost`, `meme`, `penis`, `vagina`, `jpeg`, `isnowillegal`, `gif`")
            embed.add_field(name="Economy", value="`register`, `balance`, `daily`, more soon...")

            embed.add_field(name="NSFW",
                            value="`pgif`, `4k`, `phsearch`, `lewdneko`, `yandere`, `boobs`, `ass`, `cumsluts`, `lingerie`,"
                              " `gonewild`, `nsfw`")

            embed.add_field(name="Reactions",
                            value="`hug`, `kiss`, `pat`, `cuddle`, `tickle`, `bite`, `slap`, `punch`,"
                                    "`poke`, `nom`, `lick`, `lewd`, `trap`, `owo`, `wasted`, `banghead`,"
                                    "`discordmeme`, `stare`, `thinking`, `dab`, `kemonomimi`, `why`")
            embed.add_field(name="Game Stats",
                            value="`osu`, `r6`")
        except Exception as e:
            await ctx.send(e)

        await ctx.send(embed=embed)
        try:
            await ctx.message.add_reaction(':NekoCookie:')
        except:
            pass

def setup(bot):
    bot.remove_command('help')
    bot.add_cog(General(bot))
