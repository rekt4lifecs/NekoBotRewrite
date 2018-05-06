from discord.ext import commands
import discord
import logging, re, math
import lavalink
import config
import json

time_rx = re.compile('[0-9]+')

# Languages
languages = ["english", "weeb"]
english = json.load(open("lang/english.json"))
weeb = json.load(open("lang/weeb.json"))

def getlang(lang:str):
    if lang == "english":
        return english
    elif lang == "weeb":
        return weeb
    else:
        return None

class Audio:

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot,
                            host=config.lavalink['host'],
                            ws_port=8080,
                            password=config.lavalink['password'],
                            loop=self.bot.loop, log_level=logging.INFO)
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
                    await c.send('**Queue Ended**')
                    await event.player.disconnect()

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, *, query):
        """Play Something"""
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
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

        tracks = await self.bot.lavalink.get_tracks(query)

        if not tracks:
            return await ctx.send(getlang(lang)["audio"]["nothing_found"])

        embed = discord.Embed(colour=0xDEADBF)

        if 'list' in query and 'ytsearch:' not in query:
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = getlang(lang)["audio"]["playlist_enqueued"]
            embed.description = getlang(lang)["audio"]["imported_tracks"].format(len(tracks))
            await ctx.send(embed=embed)
        else:
            embed.title = getlang(lang)["audio"]["track_enqueued"]
            embed.description = f'[{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})'
            await ctx.send(embed=embed)
            player.add(requester=ctx.author.id, track=tracks[0])

        if not player.is_playing:
            await player.play()

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        """Skip a song"""
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        listx = []
        for user in ctx.author.voice.channel.members:
            listx.append(user)

        await ctx.send('⏭ | Skipped.')
        await player.skip()

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        listx = []
        for user in ctx.author.voice.channel.members:
            listx.append(user)

        player.queue.clear()
        await player.stop()
        await ctx.send('⏹ | Stopped.')

    @commands.command()
    @commands.guild_only()
    async def now(self, ctx):
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
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
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send(getlang(lang)["audio"]["no_queue"])

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

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
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        listx = []
        for user in ctx.author.voice.channel.members:
            listx.append(user)

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

        listx = []
        for user in ctx.author.voice.channel.members:
            listx.append(user)

        await player.set_volume(volume)
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @commands.command()
    @commands.guild_only()
    async def shuffle(self, ctx):
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        listx = []
        for user in ctx.author.voice.channel.members:
            listx.append(user)

        player.shuffle = not player.shuffle

        await ctx.send('🔀 | Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @commands.command()
    @commands.guild_only()
    async def repeat(self, ctx):
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        listx = []
        for user in ctx.author.voice.channel.members:
            listx.append(user)

        player.repeat = not player.repeat

        await ctx.send('🔁 | Repeat ' + ('enabled' if player.repeat else 'disabled'))

    @commands.command()
    @commands.guild_only()
    async def find(self, ctx, *, query):
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query

        tracks = await self.bot.lavalink.get_tracks(query)

        if not tracks:
            return await ctx.send(getlang(lang)["audio"]["nothing_found"])

        tracks = tracks[:10]  # First 10 results

        o = ''
        for i, t in enumerate(tracks, start=1):
            o += f'`{i}.` [{t["info"]["title"]}]({t["info"]["uri"]})\n'

        embed = discord.Embed(colour=0xDEADBF, description=o)

        await ctx.send(embed=embed)

    @commands.command(aliases=['dc'])
    @commands.guild_only()
    async def disconnect(self, ctx):
        lang = None #await self.bot.redis.get(f"{ctx.message.author.id}-lang")
        if lang:
            lang = lang.decode('utf8')
        else:
            lang = "english"
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(getlang(lang)["audio"]["not_playing"])

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send(getlang(lang)["audio"]["not_in_my_vc"])

        listx = []
        for user in ctx.author.voice.channel.members:
            listx.append(user)

        await player.disconnect()
        await ctx.send('*⃣ | Disconnected.')

def setup(bot):
    bot.add_cog(Audio(bot))