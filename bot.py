from discord.ext import commands
import discord

class NekoBot(commands.AutoShardedBot):

    def __init__(self):
        super().__init__()
