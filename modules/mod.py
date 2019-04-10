from discord.ext import commands
import discord
import rethinkdb as r
import logging
import io, os, re
import textwrap
import traceback
from contextlib import redirect_stdout
import time
import asyncio
import json
import shlex
import argparse
from collections import Counter

from .utils import helpers, checks

log = logging.getLogger()
custom_emoji = re.compile(r'<:(\w+):(\d+)>')

class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

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

    async def _has_custom_roles_enabled(self, guild: int):
        if not await r.table("customroles").get(str(guild)).run(self.bot.r_conn):
            return False
        else:
            return True

    def _get_role_from_id(self, roles: discord.Guild.roles, role_to_find):
        found = []
        for role in roles:
            if role.id == int(role_to_find):
                found.append(role)
        return found

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.group(aliases=["customrole", "role"])
    async def customroles(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @customroles.command(name="join")
    async def __join(self, ctx, *, role: discord.Role = None):
        """Join a role"""
        if not await self._has_custom_roles_enabled(ctx.guild.id):
            return await ctx.send("This server has no custom roles setup.")

        roles = (await r.table("customroles").get(str(ctx.guild.id)).run(self.bot.r_conn))["roles"]

        if not role:

            if not roles:
                return await ctx.send("No roles have been added for users to join")

            em = discord.Embed(color=0xDEADBF)
            em.title = "Available Custom Roles"
            desc = "Usage: n!customrole join <role>\n**Roles:**\n"
            newrolearray = []
            for roleId in roles:
                roleInfo = self._get_role_from_id(ctx.guild.roles, roleId)
                if roleInfo:
                    newrolearray.append(roleId)
                    desc += "{}\n".format(roleInfo[0].name)
            em.description = desc
            await ctx.send(embed=em)
            if len(roles) != len(newrolearray):
                await r.table("customroles").get(str(ctx.guild.id)).update({"roles": newrolearray}).run(self.bot.r_conn)
            return

        if str(role.id) not in roles:
            return await ctx.send("That's not a valid role I can give you ;w;")
        else:
            if role.id in [x.id for x in ctx.author.roles]:
                return await ctx.send("You already have that role")
            roleInfo = self._get_role_from_id(ctx.guild.roles, role.id)
            try:
                await ctx.author.add_roles(roleInfo[0], reason="Custom role")
                await ctx.message.add_reaction("\u2705")
            except discord.Forbidden:
                return await ctx.send("I don't have permissions to give roles to users")

    @customroles.command(name="leave")
    async def __leave(self, ctx, *, role: discord.Role):
        """Leave a role"""
        if not await self._has_custom_roles_enabled(ctx.guild.id):
            return await ctx.send("This server has no custom roles setup.")

        roles = (await r.table("customroles").get(str(ctx.guild.id)).run(self.bot.r_conn))["roles"]

        if str(role.id) not in roles:
            return await ctx.send("That's not a valid role I can remove from you ;w;")
        else:
            if role.id in [x.id for x in ctx.author.roles]:
                roleInfo = self._get_role_from_id(ctx.guild.roles, role.id)
                try:
                    await ctx.author.remove_roles(roleInfo[0], reason="Custom role")
                    await ctx.message.add_reaction("\u2705")
                except discord.Forbidden:
                    await ctx.send("I don't have permissions to remove roles from users")
            else:
                await ctx.send("You don't even have that role, how am I suppose to remove it")

    @customroles.command(name="addrole")
    @commands.has_permissions(manage_roles=True)
    async def __addrole(self, ctx, *, role: discord.Role):
        """Add a role for users to be able to join"""
        if not await self._has_custom_roles_enabled(ctx.guild.id):
            return await ctx.send("This server has no custom roles setup.")

        roles = (await r.table("customroles").get(str(ctx.guild.id)).run(self.bot.r_conn))["roles"]

        if str(role.id) in roles:
            return await ctx.send("I already have that role set for users to be able to join")
        elif role.id == ctx.guild.id:
            return await ctx.send("I can't add that role")
        newrolearray = roles
        newrolearray.append(str(role.id))
        await r.table("customroles").get(str(ctx.guild.id)).update({"roles": newrolearray}).run(self.bot.r_conn)
        await ctx.send("Added role!")

    @customroles.command(name="removerole")
    @commands.has_permissions(manage_roles=True)
    async def __removerole(self, ctx, *, role: discord.Role):
        """Remove a role from people to be able to join"""
        if not await self._has_custom_roles_enabled(ctx.guild.id):
            return await ctx.send("This server has no custom roles setup.")

        roles = (await r.table("customroles").get(str(ctx.guild.id)).run(self.bot.r_conn))["roles"]

        if str(role.id) not in roles:
            return await ctx.send("That role is already not setup for users to join")
        elif role.id == ctx.guild.id:
            return await ctx.send("I can't remove that role")
        newrolearray = []
        for roleId in roles:
            if str(roleId) != str(role.id):
                newrolearray.append(str(role.id))
        await r.table("customroles").get(str(ctx.guild.id)).update({"roles": newrolearray}).run(self.bot.r_conn)
        await ctx.send("Removed role!")

    @customroles.command(name="toggle")
    @commands.has_permissions(manage_roles=True)
    async def __toggle(self, ctx):
        """Toggle reaction roles for your server"""
        if await self._has_custom_roles_enabled(ctx.guild.id):
            await r.table("customroles").get(str(ctx.guild.id)).delete().run(self.bot.r_conn)
            await ctx.send("Removed custom roles from this server")
        else:
            await r.table("customroles").insert({
                "id": str(ctx.guild.id),
                "roles": [],
                "setupUser": str(ctx.author.id)
            }).run(self.bot.r_conn)
            await ctx.send("Enabled custom roles for this server!")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """Kicks a member from the server."""
        try:
            if reason is None:
                reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
            await member.kick(reason=reason)
            await ctx.send(embed=discord.Embed(color=0x87ff8f, description="{} has been kicked".format(member.mention)))
        except:
            await ctx.send("I couldn't do that action, either I dont have permissions or my role is too low.")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def hackban(self, ctx, member_id: int):
        """Bans a user from their ID"""
        try:
            await self.bot.http.ban(member_id, ctx.guild.id)
        except discord.NotFound:
            return await ctx.send("That user was not found.")
        except discord.Forbidden:
            return await ctx.send("I couldn't ban that user.")

        await ctx.send("\N{OK HAND SIGN}")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """Bans a member from the server."""

        try:
            if reason is None:
                reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

            await ctx.guild.ban(member, reason=reason)
            await ctx.send(embed=discord.Embed(color=0x87ff8f, description="{} has been banned".format(member.mention)))
        except:
            await ctx.send("I couldn't do that action, either I dont have permissions or my role is too low.")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def softban(self, ctx, user: discord.Member):
        """Softban a user, bans a user to delete all their messages and unbans after."""

        try:
            await ctx.guild.ban(user, reason=f"Softbanned by {ctx.author.name}", delete_message_days=7)
            await ctx.guild.unban(user)
            await ctx.send("I have successfully softbanned that user.")
        except:
            await ctx.send("I couldn't do that action, either I dont have permissions or my role is too low.")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def massban(self, ctx, reason: ActionReason, *members: MemberID):
        """Ban multiple people at once."""

        try:
            for member_id in members:
                await ctx.guild.ban(discord.Object(id=member_id), reason=reason)

            await ctx.send('\N{OK HAND SIGN}')
        except:
            await ctx.send("I couldn't do that action, either I dont have permissions or my role is too low.")

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason: ActionReason = None):
        """Unbans a member from the server."""

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.unban(member.user, reason=reason)
        await ctx.send("I have unbanned {}".format(member.user.name))

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_nicknames=True)
    async def rename(self, ctx, user: discord.Member, *, nickname=""):
        """Rename a user"""

        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await user.edit(nick=nickname)
            await ctx.send("Renamed {}".format(user.mention))
        except:
            await ctx.send("I couldn't do that action, either I dont have permissions or my role is too low.")

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
            await ctx.send("Muted user.")

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
            await ctx.send("Unmuted user.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def say(self, ctx, *, what_to_say: str):
        await ctx.send(what_to_say)

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
            await ctx.send('Loaded <a:anone:502539278841282561>')

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
            await ctx.send('Unloaded <a:anone:502539278841282561>')

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
            await ctx.send('Reloaded <a:anone:502539278841282561>')

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        s = time.time()
        msg = await ctx.send("Ping")
        await msg.edit(content="Ping, {}ms".format(round((time.time() - s) * 1000, 2)))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, *, question: str):
        """Start a poll"""
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            messages.append(await ctx.send("Say poll option or {}cancel to publish poll.".format(ctx.prefix)))

            try:
                entry = await self.bot.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith("{}cancel".format(ctx.prefix)):
                break

            answers.append((helpers.to_emoji(i), entry.clean_content))

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

    @commands.group(hidden=True, name="ipc")
    @commands.is_owner()
    async def ipc_handle(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @ipc_handle.command(name="reload")
    async def ipc_reload(self, ctx, *, module: str):
        for x in range(self.bot.instances):
            self.bot.ipc_queue.put_nowait(json.dumps({
                "op": "reload",
                "d": module
            }))
        await ctx.send("Reload added to queue")

    @ipc_handle.command(name="unload")
    async def ipc_unload(self, ctx, *, module: str):
        for x in range(self.bot.instances):
            self.bot.ipc_queue.put_nowait(json.dumps({
                "op": "unload",
                "d": module
            }))
        await ctx.send("Unload added to queue")

    @ipc_handle.command(name="load")
    async def ipc_load(self, ctx, *, module: str):
        for x in range(self.bot.instances):
            self.bot.ipc_queue.put_nowait(json.dumps({
                "op": "load",
                "d": module
            }))
        await ctx.send("Load added to queue")

    @commands.command(hidden=True, name="eval")
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

        body = helpers.cleanup_code(body)
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

    #
    #   From https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py#L730
    #
    @commands.group(aliases=["remove"])
    @commands.guild_only()
    @checks.has_permissions(manage_messages=True)
    async def purge(self, ctx):
        """Removes messages that meet a criteria."""

        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):

        if limit > 2000:
            return await ctx.send("Too many messages to search given ({}/2000)".format(limit))

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.send("Error: {} (try a smaller search?)".format(e))

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
            e = discord.Embed(color=0x87ff8f, description="Successfully removed {} messages.".format(deleted))
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
            await ctx.send("The substring length must be at least 3 characters.")
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

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send("Too many messages to search for ({}/2000)".format(search))

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(embed=discord.Embed(color=0x87ff8f,
                                           description="Successfully removed {} reactions.".format(total_reactions)))

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

        args.search = max(0, min(2000, args.search))  # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def autorole(self, ctx, *, role: discord.Role = None):
        """Sets the autorole.

        (Case sensitive)

        Example:
            n!autorole Members
            n!autorole @Members
            n!autorole "All Cuties"
        """
        guild = ctx.guild

        if not role:
            if await r.table("autorole").get(str(guild.id)).run(self.bot.r_conn):
                await r.table("autorole").get(str(guild.id)).delete().run(self.bot.r_conn)
                return await ctx.send("Reset Autorole.")
            else:
                return await ctx.send_help(ctx.command)
        else:
            data = {
                "id": str(guild.id),
                "role": str(role.id)
            }
            await r.table("autorole").get(str(guild.id)).delete().run(self.bot.r_conn)
            await r.table("autorole").insert(data).run(self.bot.r_conn)
            return await ctx.send("Updated Autorole to {}".format(role.name))

def setup(bot):
    bot.add_cog(Moderation(bot))
