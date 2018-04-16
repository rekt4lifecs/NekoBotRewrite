from discord.ext import commands
import discord, argparse, re, shlex, traceback, io, textwrap, asyncio
from .utils import checks
from contextlib import redirect_stdout
from collections import Counter
from .utils.chat_formatting import pagify, box
from .utils.hastebin import post as hastebin
import math
import string
import time
import pymysql

class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)

def millify(n):
    millnames = ['', 'k', 'M', ' Billion', ' Trillion']
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)

async def run_cmd(cmd: str) -> str:
    """Runs a subprocess and returns the output."""
    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    results = await process.communicate()
    return "".join(x.decode("utf-8") for x in results)

class Moderation:
    """Moderation Tools"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    class BannedMember(commands.Converter):
        async def convert(self, ctx, argument):
            ban_list = await ctx.guild.bans()
            try:
                member_id = int(argument, base=10)
                entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
            except ValueError:
                entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

            if entity is None:
                raise commands.BadArgument("Not a valid previously-banned member.")
            return entity

    class MemberID(commands.Converter):
        async def convert(self, ctx, argument):
            try:
                m = await commands.MemberConverter().convert(ctx, argument)
            except commands.BadArgument:
                try:
                    return int(argument, base=10)
                except ValueError:
                    raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
            else:
                can_execute = ctx.author.id == ctx.bot.owner_id or \
                              ctx.author == ctx.guild.owner or \
                              ctx.author.top_role > m.top_role

                if not can_execute:
                    raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
                return m.id

    class ActionReason(commands.Converter):
        async def convert(self, ctx, argument):
            ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'
            if len(ret) > 512:
                reason_max = 512 - len(ret) - len(argument)
                raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
            return ret

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        """Show all servers"""
        servers = sorted(list(self.bot.guilds), key=lambda s: s.name.lower())
        msg = ""
        for i, server in enumerate(servers):
            msg += "**{}** | ".format(server.name)

        for page in pagify(msg, ['\n']):
            await ctx.send(page)

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    @commands.guild_only()
    @checks.is_admin()
    async def dehoist(self, ctx):
        """Dehoister"""
        users_dehoisted = []
        users_failed = []
        starttime = int(time.time())
        await ctx.send("Dehoist started...")
        for user in ctx.message.guild.members:
            try:
                if not user.display_name[0] in list(str(string.ascii_letters)):
                    await user.edit(nick=None, reason="Hoisting")
                    users_dehoisted.append(f"{user.name}-{user.id}")
            except:
                users_failed.append(user.id)
                pass
        hastepaste = await hastebin("\n".join(users_dehoisted))
        await ctx.send(f"{len(users_dehoisted)} users dehoisted, finished in {int(time.time() - starttime)}s.\n"
                       f"{len(users_failed)} users failed to dehoist. Users dehoisted: {hastepaste}")

    @commands.command()
    @commands.is_owner()
    async def emotes(self, ctx):
        emotes = sorted(list(self.bot.emojis), key=lambda s: s.name.lower())
        msg = ""
        for i, emote in enumerate(emotes):
            msg += "**{}** | ".format(emote)

        for page in pagify(msg, ['\n']):
            await ctx.send(page)

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """Kicks a member from the server."""
        try:
            if reason is None:
                reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
            await member.kick(reason=reason)
            await ctx.send(embed=discord.Embed(color=0x87ff8f, description=f"{member.name} has been kicked."))
        except:
            await ctx.send("I couldn't kick that user, either I dont have permissions or my role is too low.")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Bans a member from the server."""
        try:
            if reason is None:
                reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

            await ctx.guild.ban(discord.Object(id=member), reason=reason)
            await ctx.send(embed=discord.Embed(color=0x87ff8f, description=f"{member.name} has been banned."))
        except:
            await ctx.send("I couldn't ban that user, either I dont have permissions or my role is too low.")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def massban(self, ctx, reason: ActionReason, *members: MemberID):
        """Mass bans multiple members from the server."""

        try:
            for member_id in members:
                await ctx.guild.ban(discord.Object(id=member_id), reason=reason)

            await ctx.send('\N{OK HAND SIGN}')
        except:
            await ctx.send("I couldn't ban that user, either I dont have permissions or my role is too low.")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason: ActionReason = None):
        """Unbans a member from the server."""

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}), previously banned for {member.reason}.')
        else:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}).')

    @commands.is_owner()
    @commands.command()
    async def presence(self, ctx, type: int, *, changeto : str):
        await ctx.send("changed")
        game = discord.Game(name=changeto, url="https://www.twitch.tv/rekt4lifecs",
                            type=type)
        await self.bot.change_presence(activity=game)

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_nicknames=True)
    async def rename(self, ctx, user : discord.Member, *, nickname =""):
        """Rename a user"""
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await user.edit(nick=nickname)
            await ctx.send(embed=discord.Embed(color=0x87ff8f, description=f"{user.name} has been renamed."))
        except:
            e = discord.Embed(color=0xff5630, title="⚠ Error",
                              description="I couldn't rename that user.")
            await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, *, member: discord.Member):
        """Mutes a user from the channel."""

        reason = f'Muted by {ctx.author} (ID: {ctx.author.id})'

        try:
            await ctx.channel.set_permissions(member, send_messages=False, reason=reason)
        except:
            await ctx.send("Failed to mute.")
        else:
            await ctx.send('Muted user.')

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, *, member: discord.Member):
        """Unmutes a user from the channel."""

        reason = f'Unmuted by {ctx.author} (ID: {ctx.author.id})'

        try:
            await ctx.channel.set_permissions(member, send_messages=True, reason=reason)
        except:
            await ctx.send("Failed to unmute.")
        else:
            await ctx.send('Unmuted user.')

    # @commands.command()
    # @commands.guild_only()
    # @checks.mod_or_permissions(manage_messages=True)
    # async def mute(self, ctx, user : discord.Member):
    #     """Mute a user from vc"""
    #     if user == ctx.message.author:
    #         await ctx.send("You can't mute yourself.")
    #     else:
    #         try:
    #             await user.edit(mute=True)
    #             await ctx.send(f"Muted {user.name}")
    #         except discord.Forbidden:
    #             await ctx.send("I don't have the permissions to do that ;-;")
    #
    # @commands.command()
    # @commands.guild_only()
    # @checks.mod_or_permissions(manage_messages=True)
    # async def unmute(self, ctx, user : discord.Member):
    #     """Unmute a user from vc"""
    #     if user == ctx.message.author:
    #         await ctx.send("You can't unmute yourself.")
    #     else:
    #         try:
    #             await user.edit(mute=False)
    #             await ctx.send(f"Unmuted {user.name}")
    #         except discord.Forbidden:
    #             await ctx.send("I don't have the permissions to do that ;-;")

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, *, what_to_say : str):
        await ctx.send(what_to_say)

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shutdown Bot"""
        await ctx.send("Bai bai")
        await self.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        module = "modules." + module
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        module = "modules." + module
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        module = "modules." + module
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    async def latency(self, ctx):
        if not ctx.message.author.id in [266277541646434305, 270133511325876224]:
            return
        xd = '\n'.join(f'Shard {shard}: '+str(round(self.bot.latencies[shard][1]*1000)) + 'ms' for shard in self.bot.shards)
        for page in pagify(xd):
            await ctx.send(page)

    @commands.command(hidden=True, aliases=['exec'])
    @commands.is_owner()
    async def shell(self, ctx, *, command: str):
        """Run stuff"""
        with ctx.typing():
            command = self.cleanup_code(command)
            result = await run_cmd(command)
            if len(result) >= 1500:
                pa = await hastebin(result)
                await ctx.send(f'`{command}`: {pa}')
            else:
                await ctx.send(f"`{command}`: ```{result}```\n")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def memory(self, ctx):
        """Get memory stats"""
        result = await run_cmd("cat /proc/meminfo | grep -A 2 MemTotal")
        text = f"```css\n" \
               f"[ Memory ]\n\n" \
               f"{result}\n```"
        await ctx.send(text)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, *, question : str):
        """Start a poll"""
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            messages.append(await ctx.send(f'Say poll option or {ctx.prefix}cancel to publish poll.'))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f'{ctx.prefix}cancel'):
                break

            answers.append((to_emoji(i), entry.clean_content))

        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass

        answer = '\n'.join(f'{keycap}: {content}' for keycap, content in answers)
        embed = discord.Embed(color=0xDEADBF,
                              description=f"```\n"
                                          f"{question}```\n\n"
                                          f"{answer}")

        actual_poll = await ctx.send(embed=embed)
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.group(aliases=['remove'])
    @commands.guild_only()
    async def purge(self, ctx):
        """Removes messages that meet a criteria.""" # RoboDanny <3
        
        if ctx.message.author.id == 137487801498337280:
            await ctx.send("😠")
            return

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=0xDEADBF,
                                  title="Purge",
                                  description="**purge embeds** - Removes messages that have embeds in them.\n"
                                              "**purge files** - Removes messages that have attachments in them.\n"
                                              "**purge all** - Removes all messages.\n"
                                              "**purge user** - Removes all messages by the member.\n"
                                              "**purge contains** - Removes all messages containing a substring.\n"
                                              "**purge bot** - Removes a bot user's messages and messages with their optional prefix.\n"
                                              "**purge emoji** - Removes all messages containing custom emoji.\n"
                                              "**purge reactions** - Removes all reactions from messages that have them.\n"
                                              "**purge custom** - A more advanced purge command.")
            await ctx.send(embed=embed)

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            e = discord.Embed(color=0x87ff8f, description=f'Successfully removed {deleted} messages.')
            await ctx.send(embed=e, delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @purge.command()
    @commands.has_permissions(manage_messages=True)
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @purge.command()
    @commands.has_permissions(manage_messages=True)
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @purge.command(name='all')
    @commands.has_permissions(manage_messages=True)
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @purge.command()
    @commands.has_permissions(manage_messages=True)
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @purge.command()
    @commands.has_permissions(manage_messages=True)
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring."""
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @purge.command(name='bot')
    @commands.has_permissions(manage_messages=True)
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.webhook_id is None and m.author.bot or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='emoji')
    @commands.has_permissions(manage_messages=True)
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<:(\w+):(\d+)>')
        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='reactions')
    @commands.has_permissions(manage_messages=True)
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(embed=discord.Embed(color=0x87ff8f,
                                           description=f'Successfully removed {total_reactions} reactions.'))

    @purge.command()
    @commands.has_permissions(manage_messages=True)
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.

        This command uses a powerful "command line" syntax.
        Thank You R.Danny

        The following options are valid.

        `--user`: A mention or name of the user to remove.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.

        Flag options (no arguments):

        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int, default=100)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any
        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        args.search = max(0, min(2000, args.search)) # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)

    @commands.command()
    @commands.is_owner()
    async def guildcheck(self, ctx):
        guild = ctx.message.guild
        channel = self.bot.get_channel(431887286246834178)
        owner = self.bot.get_user(guild.owner_id)
        embed = discord.Embed(color=0xDEADBF, title="Guild Join",
                              description=f"```\n"
                                          f"Name:       {guild.name}\n"
                                          f"Members:    {len(set(guild.members))}\n"
                                          f"Channels:   {len(guild.text_channels)}\n"
                                          f"Roles:      {len(guild.roles)}\n"
                                          f"Emojis:     {len(guild.emojis)}\n"
                                          f"Region:     {guild.region}\n"
                                          f"ID:         {guild.id}```\n"
                                          f"Owner: **{owner.name}** ({owner.id})")
        try:
            embed.set_thumbnail(url=guild.icon_url)
        except:
            pass
        await channel.send(embed=embed)

    @commands.command()
    async def traceback(self, ctx, *, reason: str):
        """Traceback Check"""
        user = ctx.message.author
        for role in user.roles:
            if role.id == 404595507554549760:
                channel = self.bot.get_channel(431987399581499403)
                embed = discord.Embed(color=0x8bff87, title="Issue Fixed", description=f"Issue fixed by {user.id}\n"
                                                                                       f"Reason:\n```\n"
                                                                                       f"{reason}```")
                await channel.send(embed=embed)
    # TODO
    # @commands.group()
    # @checks.is_admin()
    # @commands.guild_only()
    # async def config(self, ctx:commands.Context):
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #                                 # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     if ctx.invoked_subcommand is None:
    #         em = discord.Embed(color=0xDEADBF, title=f"⚙ Config Commands",
    #                            description="```\n"
    #                                        "Commands:\n\n"
    #                                        "n!config info       - View current config settings.\n"
    #                                        "n!config channel    - Set the log channel\n"
    #                                        "n!config set        - Set log settings\n"
    #                                        "n!config channel    - Set the log channel\n"
    #                                        "n!config invites    - Log invites\n"
    #                                        "n!config bans       - Log bans\n"
    #                                        "n!config kicks      - Log kicks\n"
    #                                        "n!config joins      - Log joins\n"
    #                                        "n!config edits      - Log edits\n```")
    #         return await ctx.send(embed=em)
    #
    # @config.command(name="info")
    # async def config_info(self, ctx):
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #         # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     guild = ctx.message.guild
    #     db.execute(f"SELECT log_channel, delete_invites, log_bans, log_kicks, log_joins, log_edits FROM config WHERE guild = {guild.id}")
    #     all_settings = db.fetchall()[0]
    #     if int(all_settings[0]) == 0:
    #         channel = "None"
    #     else:
    #         channel = self.bot.get_channel(int(all_settings[0]))
    #         channel = channel.name
    #     if int(all_settings[1]) == 0:
    #         delete_invites = False
    #     else:
    #         delete_invites = True
    #     if int(all_settings[2]) == 0:
    #         log_bans = False
    #     else:
    #         log_bans = True
    #     if int(all_settings[3]) == 0:
    #         log_kicks = False
    #     else:
    #         log_kicks = True
    #     if int(all_settings[4]) == 0:
    #         log_joins = False
    #     else:
    #         log_joins = True
    #     if int(all_settings[5]) == 0:
    #         log_edits = False
    #     else:
    #         log_edits = True
    #
    #     em = discord.Embed(color=0xDEADBF, title=f"⚙ Config Settings for {guild.name}",
    #                        description=f"```\n"
    #                                    f"Channel:           {channel}\n"
    #                                    f"Delete Invites:    {delete_invites}\n"
    #                                    f"Log Bans:          {log_bans}\n"
    #                                    f"Log Kicks:         {log_kicks}\n"
    #                                    f"Log Joins:         {log_joins}\n"
    #                                    f"Log Edits:         {log_edits}\n"
    #                                    f"```")
    #     await ctx.send(embed=em)
    #
    # @config.command(name="channel")
    # async def log_channel(self, ctx, channel : discord.TextChannel = None):
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #         # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     if channel is None:
    #         db.execute(f"UPDATE config SET log_channel = 0 WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         return await ctx.send("Disabled log channel.")
    #     db.execute(f"UPDATE config SET log_channel = {channel.id} WHERE guild = {ctx.message.guild.id}")
    #     connection.commit()
    #     await ctx.send(f"Updated log channel to **{channel.name}**")
    #
    # @config.command(name="invites")
    # async def delete_invites(self, ctx, delete_them:bool):
    #     """Delete invites? True/False"""
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #         # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     if delete_them is False:
    #         db.execute(f"UPDATE config SET delete_invites = false WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Disabled deletion of invites.")
    #     else:
    #         db.execute(f"UPDATE config SET delete_invites = true WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Enabled deletion of invites.")
    #
    # @config.command(name="bans")
    # async def log_bans(self, ctx, delete_them:bool):
    #     """Log Bans? True/False"""
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #         # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     if delete_them is False:
    #         db.execute(f"UPDATE config SET log_bans = false WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Disabled ban logging.")
    #     else:
    #         db.execute(f"UPDATE config SET log_bans = true WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Enabled ban logging.")
    #
    # @config.command(name="kicks")
    # async def log_kicks(self, ctx, delete_them:bool):
    #     """Log Kicks? True/False"""
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #         # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     if delete_them is False:
    #         db.execute(f"UPDATE config SET log_kicks = false WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Disabled kick logging.")
    #     else:
    #         db.execute(f"UPDATE config SET log_kicks = true WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Enabled kick logging.")
    #
    # @config.command(name="joins")
    # async def log_joins(self, ctx, delete_them:bool):
    #     """Log Joins? True/False"""
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #         # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     if delete_them is False:
    #         db.execute(f"UPDATE config SET log_joins = false WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Disabled join logging.")
    #     else:
    #         db.execute(f"UPDATE config SET log_joins = true WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Enabled join logging.")
    #
    # @config.command(name="edits")
    # async def log_edits(self, ctx, delete_them:bool):
    #     """Log Edits? True/False"""
    #     connection = pymysql.connect(host="localhost",
    #                                  user="root",
    #                                  password="rektdiscord",
    #                                  db="nekobot",
    #                                  port=3306)
    #     db = connection.cursor()
    #     if not db.execute(f"SELECT 1 FROM config WHERE guild = {ctx.message.guild.id}"):
    #         # guild | channel | delete invites | log bans | log kicks | log joins | log edits
    #         db.execute(f"INSERT INTO config VALUES ({ctx.message.guild.id}, 0, false, false, false, false, false)")
    #         connection.commit()
    #     if delete_them is False:
    #         db.execute(f"UPDATE config SET log_edits = false WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Disabled edit logging.")
    #     else:
    #         db.execute(f"UPDATE config SET log_edits = true WHERE guild = {ctx.message.guild.id}")
    #         connection.commit()
    #         await ctx.send("Enabled edit logging.")
    #
    async def on_guild_join(self, guild):
        if not guild.large:
            return
        channel = self.bot.get_channel(431887286246834178)
        owner = self.bot.get_user(guild.owner_id)
        embed = discord.Embed(color=0x8bff87, title="Guild Join",
                              description=f"```\n"
                                          f"Name:       {guild.name}\n"
                                          f"Members:    {len(set(guild.members))}\n"
                                          f"Channels:   {len(guild.text_channels)}\n"
                                          f"Roles:      {len(guild.roles)}\n"
                                          f"Emojis:     {len(guild.emojis)}\n"
                                          f"Region:     {guild.region}\n"
                                          f"ID:         {guild.id}```\n"
                                          f"Owner: **{owner.name}** ({owner.id})")
        try:
            embed.set_thumbnail(url=guild.icon_url)
        except:
            pass
        await channel.send(embed=embed)

    async def on_guild_remove(self, guild):
        if not guild.large:
            return
        channel = self.bot.get_channel(431887286246834178)
        owner = self.bot.get_user(guild.owner_id)
        embed = discord.Embed(color=0xff6f3f, title="Guild Leave",
                              description=f"```\n"
                                          f"Name:       {guild.name}\n"
                                          f"Members:    {len(set(guild.members))}\n"
                                          f"Channels    {len(guild.text_channels)}\n"
                                          f"Roles:      {len(guild.roles)}\n"
                                          f"Emojis:     {len(guild.emojis)}\n"
                                          f"Region:     {guild.region}\n"
                                          f"ID:         {guild.id}```\n"
                                          f"Owner: **{owner.name}** ({owner.id})")
        try:
            embed.set_thumbnail(url=guild.icon_url)
        except:
            pass
        await channel.send(embed=embed)
    #
    # # async def on_message_delete(self, message):
    # #     message = self.bot.get_message(messageid)
    # #     if channelid == 221989003400970241:
    # #         channel = self.bot.get_channel(431887286246834178)
    # #         embed = discord.Embed(color=0xff6f3f, title="Message Deleted",
    # #                               description=f"```\n"
    # #                                           f"Author:     {message.author}\n"
    # #                                           f"Channel:    {message.channel.name} ({message.channel.id})\n"
    # #                                           f"Reactions:  {len(message.reactions)}\n"
    # #                                           f"Content:    {message.content}\n```")
    # #         await channel.send(embed=embed)

    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        guild = before.guild
        if guild.id == 221989003400970241:
            channel = self.bot.get_channel(431887286246834178)
            embed = discord.Embed(color=0xffa230, title="Message Edited",
                                  description=f"```\n"
                                              f"Author:     {before.author}\n"
                                              f"Channel:    {before.channel.name} ({before.channel.id})\n"
                                              f"Before:     {before.content}\n"
                                              f"After:      {after.content}```")
            embed.set_footer(text=f"Edited at {after.edited_at}")
            await channel.send(embed=embed)
        # connection = pymysql.connect(host="localhost",
        #                              user="root",
        #                              password="rektdiscord",
        #                              db="nekobot",
        #                              port=3306)
        # db = connection.cursor()
        # if db.execute(f"SELECT 1 FROM config WHERE guild = {guild.id}"):
        #     try:
        #         db.execute(f"SELECT log_channel FROM config WHERE guild {guild.id}")
        #         channel = int(db.fetchone()[0])
        #         channel = self.bot.get_channel(channel)
        #         embed = discord.Embed(color=0xffa230, title=f"Message Edited - {before.author.name}")
        #         embed.add_field(name="Before", value=before.content)
        #         embed.add_field(name="After", value=after.content)
        #         await channel.send(embed=embed)
        #     except Exception as e:
        #         print(e)

def setup(bot):
    bot.add_cog(Moderation(bot))