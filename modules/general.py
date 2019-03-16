import discord
from models import Context

async def _help(ctx: Context, args):
    """View the bots help"""
    await ctx.send("owo")

commands = {
    "help": _help
}
