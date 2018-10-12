from discord.ext import commands
import discord, argparse, os, shlex, traceback, io, textwrap, asyncio, re
from .utils import checks, chat_formatting
from contextlib import redirect_stdout
from collections import Counter
from .utils.hastebin import post as hastebin
import math
import string
import time
import config
import aiohttp
import re, gettext, inspect, datetime, collections
import logging
import rethinkdb as r

log = logging.getLogger()

invite_rx = re.compile("discord(?:app)?\.(?:gg|com|me\/invite)\/([a-z0-9]{1,16})", re.IGNORECASE)

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

        # The following is for the new repl
        self.repl_sessions = {}
        self.repl_embeds = {}
        self.lang = {}
        # self.languages = ["french", "polish", "spanish", "tsundere", "weeb"]
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("mod", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

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
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.guild_only()
    @checks.is_admin()
    async def dehoist(self, ctx):
        """Dehoister"""
        _ = await self._get_text(ctx)
        users_dehoisted = []
        users_failed = []
        starttime = int(time.time())
        await ctx.send(_("Starting dehoist..."))
        for user in ctx.message.guild.members:
            try:
                if not user.display_name[0] in list(str(string.ascii_letters)):
                    await user.edit(nick="Hoister", reason="Hoisting")
                    users_dehoisted.append(f"{user.name}-{user.id}")
            except:
                users_failed.append(user.id)
                pass
        hastepaste = await hastebin("\n".join(users_dehoisted))
        await ctx.send(_("%s users dehoisted in %s,\n"
                         "%s users failed to dehoist,\n"
                         "Users Dehoisted: %s") % (len(users_dehoisted), int(time.time() - starttime), len(users_failed), hastepaste))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(5, 10, commands.BucketType.user)
    @checks.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """Kicks a member from the server."""
        _ = await self._get_text(ctx)
        try:
            if reason is None:
                reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
            await member.kick(reason=reason)
            await ctx.send(embed=discord.Embed(color=0x87ff8f, description=_("%s has been kicked") % member.mention))
        except:
            await ctx.send(_("I couldn't do that action, either I dont have permissions or my role is too low."))

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def hackban(self, ctx, member_id:int):
        """Bans a user from their ID"""
        _ = await self._get_text(ctx)
        try:
            await self.bot.http.ban(member_id, ctx.guild.id)
        except discord.NotFound:
            return await ctx.send(_("That user was not found."))
        except discord.Forbidden:
            return await ctx.send(_("I couldn't ban that user."))

        await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """Bans a member from the server."""
        _ = await self._get_text(ctx)
        try:
            if reason is None:
                reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

            await ctx.guild.ban(member, reason=reason)
            await ctx.send(embed=discord.Embed(color=0x87ff8f, description=_("%s has been banned") % member.mention))
        except:
            await ctx.send(_("I couldn't do that action, either I dont have permissions or my role is too low."))

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def softban(self, ctx, user:discord.Member):
        """Softban a user, bans a user to delete all their messages and unbans after."""

        _ = await self._get_text(ctx)

        try:
            await ctx.guild.ban(user, reason=f"Softbanned by {ctx.author.name}", delete_message_days=7)
            await ctx.guild.unban(user)
            await ctx.send(_("I have successfully softbanned that user."))
        except:
            await ctx.send(_("I couldn't do that action, either I dont have permissions or my role is too low."))

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def massban(self, ctx, reason: ActionReason, *members: MemberID):
        """Ban multiple people at once."""
        _ = await self._get_text(ctx)
        try:
            for member_id in members:
                await ctx.guild.ban(discord.Object(id=member_id), reason=reason)

            await ctx.send('\N{OK HAND SIGN}')
        except:
            await ctx.send(_("I couldn't do that action, either I dont have permissions or my role is too low."))

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason: ActionReason = None):
        """Unbans a member from the server."""
        _ = await self._get_text(ctx)
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.unban(member, reason=reason)
        await ctx.send(_("I have unbanned %s") % member)

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_nicknames=True)
    async def rename(self, ctx, user : discord.Member, *, nickname =""):
        """Rename a user"""
        _ = await self._get_text(ctx)
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await user.edit(nick=nickname)
            await ctx.send(_("Renamed %s") % user)
        except:
            e = discord.Embed(color=0xff5630, title="⚠ Error",
                              description=_("I couldn't do that action, either I dont have permissions or my role is too low."))
            await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, *, member: discord.Member):
        """Mutes a user from the channel."""

        reason = f'Muted by {ctx.author} (ID: {ctx.author.id})'
        _ = await self._get_text(ctx)

        try:
            await ctx.channel.set_permissions(member, send_messages=False, reason=reason)
        except:
            await ctx.send(_("Failed to mute."))
        else:
            await ctx.send(_("Muted user."))

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, *, member: discord.Member):
        """Unmutes a user from the channel."""

        reason = f'Unmuted by {ctx.author} (ID: {ctx.author.id})'
        _ = await self._get_text(ctx)

        try:
            await ctx.channel.set_permissions(member, send_messages=True, reason=reason)
        except:
            await ctx.send(_("Failed to unmute."))
        else:
            await ctx.send(_("Unmuted user."))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def say(self, ctx, *, what_to_say : str):
        await ctx.send(what_to_say)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shutdown Bot"""
        await ctx.send("Bai bai")
        await self.bot.close()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        module = "modules." + module
        try:
            self.bot.load_extension(module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('Loaded <a:forsenPls:444882132343717898>')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        module = "modules." + module
        try:
            self.bot.unload_extension(module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('Unloaded <a:forsenPls:444882132343717898>')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        if module == "all":
            for file in os.listdir("modules"):
                if file.endswith(".py"):
                    name = file[:-3]
                    try:
                        self.bot.unload_extension(f"modules.{name}")
                        self.bot.load_extension(f"modules.{name}")
                    except:
                        log.warning("Failed to load {}.".format(name))
                        traceback.print_exc()

            return await ctx.send("Reloaded all.")

        module = "modules." + module
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('Reloaded <a:forsenPls:444882132343717898>')

    @commands.command(aliases=["ping"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def latency(self, ctx):
        """Get bot latency across all shards"""
        msg = ""
        for x in range(self.bot.shard_count):
            ping = await self.bot.redis.get(f"shard:{x}")
            msg += f"Shard {x+1}: {ping.decode('utf8')}\n"

        for i in chat_formatting.pagify(msg, page_length=1750):
            await ctx.send(i)

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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def screenshot(self, ctx, *, url: str):
        """Get screenshots of a webpage"""
        with ctx.typing():
            await run_cmd("python3.6 screenshot.py %s" % url)
            await ctx.send(file=discord.File("ss.png", filename="screenshot.png"))
            os.remove("ss.png")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, *, question : str):
        """Start a poll"""
        messages = [ctx.message]
        answers = []

        _ = await self._get_text(ctx)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            messages.append(await ctx.send(_("Say poll option or %scancel to publish poll.") % ctx.prefix))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(_("%scancel") % ctx.prefix):
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

    async def on_message_delete(self, message):
        finishedmsg = invite_rx.sub("[INVITE]", message.content)
        try:
            optin = await self.bot.redis.get(f"{message.author.id}-snipe")
            if optin is not None:
                if optin.decode('utf-8') == "false":
                    return
            await self.bot.redis.set(f"snipe:{message.channel.id}:author", message.author.name)
            await self.bot.redis.set(f"snipe:{message.channel.id}:content", finishedmsg)
        except:
            pass

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def snipe(self, ctx, optin:bool = None):
        """Snipe the last message."""
        await ctx.trigger_typing()
        if optin is not None:
            if optin:
                boolValue = "true"
            else:
                boolValue = "false"
            await self.bot.redis.set(f"{ctx.message.author.id}-snipe", boolValue)
            return await ctx.send(f"**Snipe opt status updated to** `{boolValue}`")
        if not await self.bot.redis.get(f"snipe:{ctx.message.channel.id}:content"):
            return await ctx.send("**No message found to snipe.**")
        else:
            try:
                msg = await self.bot.redis.get(f"snipe:{ctx.message.channel.id}:content")
                author = await self.bot.redis.get(f"snipe:{ctx.message.channel.id}:author")
                em = discord.Embed(color=0xDEADBF, title="From %s" % author.decode("utf8"))
                em.description = "```\n%s\n```" % msg.decode("utf8")
                em.set_footer(text="Sniped by %s" % ctx.author.name)
                return await ctx.send(embed=em)
            except:
                return await ctx.send(f"**Failed to get message.**")

    @commands.group(aliases=['remove'])
    @commands.guild_only()
    @checks.has_permissions(manage_messages=True)
    async def purge(self, ctx):
        """Removes messages that meet a criteria."""

        _ = await self._get_text(ctx)

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=0xDEADBF,
                                  title="Purge",
                                  description=_("**purge embeds** - Removes messages that have embeds in them.\n"
                                              "**purge files** - Removes messages that have attachments in them.\n"
                                              "**purge all** - Removes all messages.\n"
                                              "**purge user** - Removes all messages by the member.\n"
                                              "**purge contains** - Removes all messages containing a substring.\n"
                                              "**purge bot** - Removes a bot user's messages and messages with their optional prefix.\n"
                                              "**purge emoji** - Removes all messages containing custom emoji.\n"
                                              "**purge reactions** - Removes all reactions from messages that have them.\n"
                                              "**purge custom** - A more advanced purge command."))
            await ctx.send(embed=embed)

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        _ = await self._get_text(ctx)
        if limit > 2000:
            return await ctx.send(_("Too many messages to search given (%s/2000)") % limit)

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send(_("I do not have permissions to delete messages."))
        except discord.HTTPException as e:
            return await ctx.send(_("Error: %s (try a smaller search?)") % e)

        try:
            await ctx.message.delete()
        except:
            pass

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            e = discord.Embed(color=0x87ff8f, description=_("Successfully removed %s messages.") % deleted)
            await ctx.send(embed=e, delete_after=4)
        else:
            await ctx.send(to_send, delete_after=4)

    @purge.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @purge.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @purge.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @purge.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @purge.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring."""

        if len(substr) < 3:
            _ = await self._get_text(ctx)
            await ctx.send(_("The substring length must be at least 3 characters."))
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @purge.command(name='bot')
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.webhook_id is None and m.author.bot or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='emoji')
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<:(\w+):(\d+)>')
        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""
        _ = await self._get_text(ctx)

        if search > 2000:
            return await ctx.send(_("Too many messages to search for (%s/2000)") % search)

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(embed=discord.Embed(color=0x87ff8f,
                                           description=_("Successfully removed %s reactions.") % total_reactions))

    @purge.command()
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.

        This command uses a powerful "command line" syntax.
        >w<

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

    async def on_guild_join(self, guild):
        if not guild.large:
            return
        log.info(f"Joined Large Guild, {guild.name} ({guild.id}), {len(set(guild.members))} members")
        try:
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
            async with aiohttp.ClientSession() as cs:
                webhook = discord.Webhook.from_url(f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}",
                                                   adapter=discord.AsyncWebhookAdapter(cs))
                await webhook.send(embed=embed)
        except:
            pass

    # the following code is used with permissions from ry00001#3487.
    # https://github.com/ry00001/Erio/blob/master/extensions/eshell.py
    # (modified)
    @commands.group(invoke_without_command=True, name="weebpl", hidden=True)
    @commands.is_owner()
    async def repl(self, ctx, *, name: str = None):
        """New stylish repl command"""
        session = ctx.message.channel.id

        embed = discord.Embed(
            description="_Enter code to execute or evaluate. "
                        "`exit()` or `quit` to exit._",
            timestamp=datetime.datetime.now())

        embed.set_footer(
            text="Interactive Python Shell",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb"
                     "/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext"
                     ".svg.png")

        if name is not None:
            embed.title = name.strip(" ")

        history = collections.OrderedDict()

        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'discord': discord,
            '_': None
        }

        if session in self.repl_sessions:
            return await ctx.send('There already is a repl in this channel.')

        shell = await ctx.send(embed=embed)

        self.repl_sessions[session] = shell
        self.repl_embeds[shell] = embed

        while True:
            response = await self.bot.wait_for(
                'message',
                # formatting hard
                check=lambda m: m.content.startswith(
                    '`') and m.author == ctx.author and m.channel == ctx.channel
            )

            cleaned = self.cleanup_code(response.content)
            shell = self.repl_sessions[session]

            # Regular Bot Method
            try:
                await ctx.message.channel.get_message(
                    self.repl_sessions[session].id)
            except discord.NotFound:
                new_shell = await ctx.send(embed=self.repl_embeds[shell])
                self.repl_sessions[session] = new_shell

                embed = self.repl_embeds[shell]
                del self.repl_embeds[shell]
                self.repl_embeds[new_shell] = embed

                shell = self.repl_sessions[session]

            try:
                await response.delete()
            except discord.Forbidden:
                pass

            if len(self.repl_embeds[shell].fields) >= 7:
                self.repl_embeds[shell].remove_field(0)

            if cleaned in ('quit', 'exit', 'exit()', 'stop', 'stop()'):
                self.repl_embeds[shell].color = 16426522

                if self.repl_embeds[shell].title is not discord.Embed.Empty:
                    history_string = "History for {}\n\n\n".format(
                        self.repl_embeds[shell].title)
                else:
                    history_string = "History for latest session\n\n\n"

                for item in history.keys():
                    history_string += ">>> {}\n{}\n\n".format(
                        item,
                        history[item])

                haste_url = await hastebin(history_string)
                return_msg = f"[`Leaving shell session. History hosted on " \
                             f"hastebin.`]({haste_url}) "

                self.repl_embeds[shell].add_field(
                    name="`>>> {}`".format(cleaned),
                    value=return_msg,
                    inline=False)

                await self.repl_sessions[session].edit(
                    embed=self.repl_embeds[shell])

                del self.repl_embeds[shell]
                del self.repl_sessions[session]
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as err:
                    self.repl_embeds[shell].color = 15746887

                    return_msg = self.get_syntax_error(err)

                    history[cleaned] = return_msg

                    if len(cleaned) > 800:
                        cleaned = "<Too big to be printed>"
                    if len(return_msg) > 800:
                        haste_url = await hastebin(return_msg)
                        return_msg = f'[`SyntaxError too big to be printed. ' \
                                     f'Hosted on hastebin.`]({haste_url}) '

                    self.repl_embeds[shell].add_field(
                        name="`>>> {}`".format(cleaned),
                        value=return_msg,
                        inline=False)

                    await self.repl_sessions[session].edit(
                        embed=self.repl_embeds[shell])
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            # noinspection PyBroadException
            try:
                with redirect_stdout(stdout):
                    # probably fine
                    # noinspection PyUnboundLocalVariable
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception:
                self.repl_embeds[shell].color = 15746887
                value = stdout.getvalue()
                fmt = '```py\n{}{}\n```'.format(
                    value,
                    traceback.format_exc())
            else:
                self.repl_embeds[shell].color = 4437377

                value = stdout.getvalue()

                if result is not None:
                    fmt = '```py\n{}{}\n```'.format(
                        value,
                        result)

                    variables['_'] = result
                elif value:
                    fmt = '```py\n{}\n```'.format(value)

            history[cleaned] = fmt

            if len(cleaned) > 800:
                cleaned = "<Too big to be printed>"

            try:
                if fmt is not None:
                    if len(fmt) >= 800:
                        haste_url = await hastebin(fmt)
                        self.repl_embeds[shell].add_field(
                            name="`>>> {}`".format(cleaned),
                            value=f"[`Content too big to be printed. Hosted "
                                  f"on hastebin.`]({haste_url})",
                            inline=False)

                        await self.repl_sessions[session].edit(
                            embed=self.repl_embeds[shell])
                    else:
                        self.repl_embeds[shell].add_field(
                            name="`>>> {}`".format(cleaned),
                            value=fmt,
                            inline=False)

                        await self.repl_sessions[session].edit(
                            embed=self.repl_embeds[shell])
                else:
                    self.repl_embeds[shell].add_field(
                        name="`>>> {}`".format(cleaned),
                        value="_`No response`_",
                        inline=False)

                    await self.repl_sessions[session].edit(
                        embed=self.repl_embeds[shell])

            except discord.Forbidden:
                pass

            except discord.HTTPException as err:
                error_embed = discord.Embed(
                    color=15746887,
                    description='**Error**: _{}_'.format(err))
                await ctx.send(embed=error_embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def autorole(self, ctx, role:discord.Role=None):
        """Sets the autorole.

        (Case sensitive)

        Example:
            n!autorole Members
            n!autorole @Members
            n!autorole "All Cuties"
        """
        guild = ctx.guild
        _ = await self._get_text(ctx)
        if not role:
            if await r.table("autorole").get(str(guild.id)).run(self.bot.r_conn):
                await r.table("autorole").get(str(guild.id)).delete().run(self.bot.r_conn)
                return await ctx.send(_("Reset Autorole."))
            else:
                return await self.bot.send_cmd_help(ctx)
        else:
            data = {
                "id": str(guild.id),
                "role": str(role.id)
            }
            await r.table("autorole").get(str(guild.id)).delete().run(self.bot.r_conn)
            await r.table("autorole").insert(data).run(self.bot.r_conn)
            return await ctx.send(_("Updated Autorole to %s") % role.name)

    async def on_guild_remove(self, guild):
        if not guild.large:
            return
        log.info(f"Left Large Guild, {guild.name} ({guild.id}), {len(set(guild.members))} members")
        try:
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
            async with aiohttp.ClientSession() as cs:
                webhook = discord.Webhook.from_url(f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}",
                                                   adapter=discord.AsyncWebhookAdapter(cs))
                await webhook.send(embed=embed)
        except:
            pass

def setup(bot):
    bot.add_cog(Moderation(bot))
