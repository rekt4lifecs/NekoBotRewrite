from discord.ext import commands
from logging import INFO as loginfo
from math import ceil
from .utils.hastebin import post as haste
import discord
import re
import lavalink
import config
import json

time_rx = re.compile('[0-9]+')

# Languages
languages = ["english", "weeb", "tsundere"]
english = json.load(open("lang/english.json"))
weeb = json.load(open("lang/weeb.json"))
tsundere = json.load(open("lang/tsundere.json"))

def getlang(lang:str):
    if lang == "english":
        return english
    elif lang == "weeb":
        return weeb
    elif lang == "tsundere":
        return tsundere
    else:
        return None

class Audio:

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot,
                            host="0.0.0.0",
                            ws_port=3232,
                            password=config.lavalink['password'],
                            loop=self.bot.loop, log_level=loginfo)
            self.bot.lavalink.register_hook(self.track_hook)

    async def track_hook(self, event):
        if isinstance(event, lavalink.Events.TrackStartEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    if event.player.connected_channel:
                        if len(event.player.connected_channel.members) <= 1:
                            await event.player.stop()
                            await event.player.disconnect()
                            return await c.send("**Leaving due to nobody being in the vc channel.**")
                    embed = discord.Embed(colour=0xDEADBF, title='Now Playing',
                                          description=event.track.title)
                    embed.set_thumbnail(url=event.track.thumbnail)
                    await c.send(embed=embed)
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)

            if c:
                await c.send('**Queue Ended**')
                await event.player.disconnect()

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, *, query):
        """Play Something"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"

        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send(getlang(lang)["audio"]["join_voice"])

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send(getlang(lang)["audio"]["bot_missing_perms"])

            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send(getlang(lang)["audio"]["join_bot"])

        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        audio_data = await self.bot.lavalink.get_tracks(query)

        if not audio_data or not audio_data['tracks']:
            return await ctx.send(getlang(lang)["audio"]["nothing_found"])

        embed = discord.Embed(colour=0xDEADBF)

        if audio_data['isPlaylist']:
            tracks = audio_data['tracks']

            toplay = []
            removedtracks = 0

            for track in tracks:
                if not track["info"]["length"] >= 2700000:
                    toplay.append(track)
                else:
                    removedtracks += 1

            for track in toplay:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Enqueued!"
            if not removedtracks >= 1:
                embed.description = f"{audio_data['playlistInfo']['name']} - {len(tracks)} tracks"
            else:
                embed.description = f"{audio_data['playlistInfo']['name']} - {len(tracks)} tracks (Removed {removedtracks} track(s) for being over 45 minutes.)"
            await ctx.send(embed=embed)
        else:
            track = audio_data['tracks'][0]
            if track["info"]["length"] >= 2700000:
                em = discord.Embed(color=0xDEADBF, title="Error", description="Tracks must be at least under 45 minutes.")
                return await ctx.send(embed=em)
            embed.title = "Track Enqueued"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            await ctx.send(embed=embed)
            player.add(requester=ctx.author.id, track=track)

        if not player.is_playing:
            await player.play()

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        """Skip a song"""
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        await ctx.send('⏭ | Skipped.')
        await player.skip()

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        player.queue.clear()
        await player.stop()
        await ctx.send('⏹ | Stopped.')

    @commands.command()
    @commands.guild_only()
    async def now(self, ctx):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)
        song = 'Nothing'

        if player.current:
            pos = lavalink.Utils.format_time(player.position)
            if player.current.stream:
                dur = 'LIVE'
            else:
                dur = lavalink.Utils.format_time(player.current.duration)
            song = f'**[{player.current.title}]({player.current.uri})**\n({pos}/{dur})'

        embed = discord.Embed(colour=0xDEADBF, title=getlang(lang)["audio"]["now_playing"], description=song)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx, page: int = 1):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send(getlang(lang)["audio"]["no_queue"])

        items_per_page = 10
        pages = ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''

        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=0xDEADBF,
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        if player.paused:
            await player.set_pause(False)
            await ctx.send('⏯ | Resumed')
        else:
            await player.set_pause(True)
            await ctx.send('⏯ | Paused')

    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx, volume: int = None):
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')

        await player.set_volume(volume)
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @commands.command()
    @commands.guild_only()
    async def shuffle(self, ctx):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        player.shuffle = not player.shuffle

        await ctx.send('🔀 | Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @commands.command()
    @commands.guild_only()
    async def repeat(self, ctx):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        player.repeat = not player.repeat

        await ctx.send('🔁 | Repeat ' + ('enabled' if player.repeat else 'disabled'))

    @commands.command()
    @commands.guild_only()
    async def find(self, ctx, *, query):
        """Find songs (not playing them)"""

        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query

        results = await self.bot.lavalink.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send(getlang(lang)["audio"]["nothing_found"])

        tracks = results['tracks'][:10]  # First 10 results

        o = ''
        for i, t in enumerate(tracks, start=1):
            o += f'`{i}.` [{t["info"]["title"]}]({t["info"]["uri"]})\n'

        embed = discord.Embed(colour=0xDEADBF, description=o)

        await ctx.send(embed=embed)

    @commands.command(aliases=['dc'])
    @commands.guild_only()
    async def disconnect(self, ctx):
        lang = await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send(getlang(lang)["audio"]["not_in_my_vc"])

        await player.disconnect()
        await ctx.send('*⃣ | Disconnected.')

def setup(bot):
    bot.add_cog(Audio(bot))