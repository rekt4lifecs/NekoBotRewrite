import discord
from models import Command, Context
from .utils.cooldown import Cooldown
from .utils.checks import has_permissions, is_owner
import time

async def _help(ctx: Context, *args):
    """View the bots help"""
    if len(args) == 0:
        em = discord.Embed(color=0xDEADBF, title="NekoBot Help")
        for cmd in ctx.bot.commands:
            em.add_field(name=cmd.title(), value=", ".join(["`{}`".format(x.name) for x in ctx.bot.commands[cmd] if not x.hidden]))
        await ctx.send(embed=em)

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

commands = [
    Command(_help, name="help"),
    ping,
    Command(unload, hidden=True),
    Command(load, hidden=True),
    Command(reload, hidden=True)
]
