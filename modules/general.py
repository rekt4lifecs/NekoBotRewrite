import discord
from models import Context, Command
import time

async def _help(ctx: Context, args):
    """View the bots help"""
    await ctx.send("owo")

async def ping(ctx: Context, args):
    """Pong!"""
    s = time.time()
    msg = await ctx.send("Ping")
    await msg.edit(content="Ping, {}ms".format(round((time.time() - s) * 1000, 2)))

commands = [
    Command(_help, hidden=True, name="help"),
    ping
]
