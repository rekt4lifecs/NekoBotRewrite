import discord
from models import Context
import time

async def _help(ctx: Context, args):
    """View the bots help"""
    await ctx.send("owo")

async def ping(ctx: Context, args):
    s = time.time()
    msg = await ctx.send("Ping")
    await msg.edit(content="Ping, {}ms".format(round((time.time() - s) * 1000, 2)))

commands = {
    "help": _help,
    "ping": ping
}
