from discord.ext import commands
import discord
import logging, re
import lavalink
import config

time_rx = re.compile('[0-9]+')

class Audio:

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot, password=config.lavalink['password'], loop=self.bot.loop, log_level=logging.INFO)
            self.bot.lavalink.register_hook(self.track_hook)

    async def track_hook(self, event):
        if isinstance(event, lavalink.Events.TrackStartEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    embed = discord.Embed(colour=0xDEADBF,
                                          title='Now Playing',
                                          description=event.track.title)
                    embed.set_thumbnail(url=event.track.thumbnail)
                    await c.send(embed=embed)
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    await c.send('Queue ended! Why not queue more songs?')

def setup(bot):
    bot.add_cog(Audio(bot))