import discord
from models import Command, Context
from .utils.cooldown import Cooldown
from .utils.checks import has_permissions, is_owner
import time

async def _help(ctx: Context, *args):
    """View the bots help"""
    cmd = ctx.bot.get_command(args[0])
    if len(args) == 0 or not cmd:
        em = discord.Embed(color=0xDEADBF, title="NekoBot Help")
        for cmd in ctx.bot.commands:
            em.add_field(name=cmd.title(), value=", ".join(["`{}`".format(x.name) for x in ctx.bot.commands[cmd] if not x.hidden]))
        await ctx.send(embed=em)
    else:
        ctx.command = cmd
        await ctx.bot.send_cmd_help(ctx)

async def ping(ctx: Context, *args):
    """Pong!"""
    s = time.time()
    msg = await ctx.send("Ping")
    await msg.edit(content="Ping, {}ms".format(round((time.time() - s) * 1000, 2)))

@is_owner()
async def unload(ctx: Context, *args):
    if not len(args) > 0:
        return await ctx.bot.send_cmd_help(ctx, "<name>")
    ctx.bot.unload_extension(args[0])
    await ctx.send("Unloaded {}".format(args[0]))

@is_owner()
async def load(ctx: Context, *args):
    if not len(args) > 0:
        return await ctx.bot.send_cmd_help(ctx, "<name>")
    ctx.bot.load_extension(args[0])
    await ctx.send("Loaded {}".format(args[0]))

@is_owner()
async def reload(ctx: Context, *args):
    if not len(args) > 0:
        return await ctx.bot.send_cmd_help(ctx, "<name>")
    ctx.bot.unload_extension(args[0])
    ctx.bot.load_extension(args[0])
    await ctx.send("Reloaded {}".format(args[0]))

@Cooldown(3)
async def delprefix(ctx: Context, *args):
    """Delete or reset your prefix"""
    await ctx.bot.redis.delete(f"{ctx.author.id}-prefix")
    await ctx.send("Deleted your prefix and reset it back to the default `n!`")

@Cooldown(3)
async def prefix(ctx: Context, *args):
    """Get the bots current prefix."""
    currprefix = await ctx.bot.redis.get(f"{ctx.author.id}-prefix")
    if currprefix:
        return await ctx.send("Your custom prefix is set to `{}`".format(currprefix.decode("utf8")))
    return await ctx.send("My prefix is `n!` or `N!`")

@Cooldown(3)
async def invite(ctx, *args):
    """Get the bots invite"""
    await ctx.send("**Invite the bot:** <https://uwu.whats-th.is/32dde7>\n**Support Server:** <https://discord.gg/q98qeYN>")

commands = [
    Command(_help, name="help"),
    ping,
    Command(unload, hidden=True),
    Command(load, hidden=True),
    Command(reload, hidden=True),
    Command(delprefix, aliases=["deleteprefix", "resetprefix"]),
    prefix
]
