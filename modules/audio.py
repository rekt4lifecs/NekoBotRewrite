from discord.ext import commands
import discord
import asyncio, aiohttp

import lavalink
import config
import logging, re

import rethinkdb as r

from .utils.helpers import clean_text

log = logging.getLogger()
url_rx = re.compile("https?:\/\/(?:www\.)?.+")

ll_headers = {
    "Authorization": config.lavalink_token
}

class Audio(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, "lavalink"):
            log.info("Loaded lavalink")
            self.bot.loop.create_task(self.__post_to_hook("Loaded lavalink"))
            lavalink.Client(bot=bot, host=config.lava_host, password=config.lava_pass, loop=bot.loop,
                            rest_port=2343, ws_port=2343)

        if not self.bot.lavalink.hooks:
            log.info("Registering hook")
            self.bot.loop.create_task(self.__post_to_hook("Registered hook"))
            self.bot.lavalink.register_hook(self._track_hook)

    async def __post_to_hook(self, message):
        async with aiohttp.ClientSession() as cs:
            await cs.post(config.lavalink_hook, json={
                "embeds": [{
                    "title": "Lavalonk - %s" % self.bot.instance,
                    "description": message,
                    "color": 0xDEADBF
                }]
            })

    def cog_unload(self):
        log.info("Unloading audio")
        self.bot.loop.create_task(self.__post_to_hook("Unloaded"))
        for guild_id, player in self.bot.lavalink.players:
            self.bot.loop.create_task(player.disconnect())
            player.cleanup()
        self.bot.lavalink.players.clear()
        self.bot.lavalink.unregister_hook(self._track_hook)
        self.bot.lavalink.hooks.clear()
        del self.bot.lavalink

    async def _track_hook(self, event):
        if isinstance(event, lavalink.Events.StatsUpdateEvent):
            log.info("Lavalink Stats: CPU Load - %s | "
                     "Playing Players: %s | "
                     "Uptime: %s" % (event.stats.cpu.lavalink_load, event.stats.playing_players,
                                     lavalink.Utils.format_time(event.stats.uptime)))
            return

        channel = self.bot.get_channel(event.player.fetch("channel"))
        if not channel:
            return

        if isinstance(event, lavalink.Events.TrackStuckEvent):
            await self.__post_to_hook("Track stuck for %s" % channel.id)
            log.warning("Track stuck for %s" % channel.id)
        elif isinstance(event, lavalink.Events.TrackExceptionEvent):
            if event.player.current.author == "LISTEN.moe":
                self.bot.loop.create_task(self._retry_lmoe(event))
        elif isinstance(event, lavalink.Events.TrackEndEvent):
            if len(event.player.connected_channel.members) <= 1:
                event.player.queue.clear()
                await event.player.disconnect()
                return await channel.send("Stopping due to nobody else in the channel")
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            event.player.queue.clear()
            await event.player.disconnect()
        else:
            await self.__post_to_hook(str(type(event).__name__))

    async def _retry_lmoe(self, event):
        await asyncio.sleep(1.5)
        if event.player.is_connected:
            event.player.queue.clear()
            track = (await self.bot.lavalink.get_tracks("https://listen.moe/stream"))["tracks"][0]
            event.player.add(requester=1, track=track)
            await self.__post_to_hook("Retrying LISTEN.moe...")
            await event.player.play()

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def play(self, ctx, *, query: str):

        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in any voice channel ;w;")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send("Missing permissions to connect or speak ;w;")
            player.store("channel", ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("Join my voice channel you baka")

        if len(player.queue) > 50:
            return await ctx.send("You are too much songs in your queue you baka")

        query = query.strip("<>")

        if not url_rx.match(query):
            query = "ytsearch:" + query
        elif "osu.ppy.sh/beatmapsets" in query or "hentaihaven.org/" in query:
            await ctx.trigger_typing()
            if "hentaihaven" in query and not ctx.channel.is_nsfw():
                return await ctx.send("This is not an nsfw channel hmph shouldn't be posting that here >:|")
            data = {"url": query}
            async with aiohttp.ClientSession() as cs:
                async with cs.post("https://lava.nekobot.xyz/api", json=data, headers=ll_headers) as res:
                    res = await res.json()
            if not res["message"].startswith("http"):
                return await ctx.send("Failed to get data ;w;")
            query = res["message"]

        results = await self.bot.lavalink.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("I found nothing ;w;")

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            if len(tracks) > 50:
                return await ctx.send("Too much tracks in this playlist ;w;")
            elif (len(tracks) + len(player.queue)) > 50:
                return await ctx.send("Too much in queue already ;w;")

            for track in tracks:
                if not track["info"]["length"] > 3600000:
                    player.add(requester=ctx.author.id, track=track)

            await ctx.send("Added playlist **%s**" % clean_text(results["playlistInfo"]["name"]))
        else:
            if len(results["tracks"]) < 2:
                track = results["tracks"][0]
                if track["info"]["length"] > 3600000:
                    return await ctx.send("Thats too long for me to play baka")
                await ctx.send("Added **%s** to queue" % clean_text(track["info"]["title"]))
                player.add(requester=ctx.author.id, track=track)
            else:
                tracks = results["tracks"][:5]
                msg = "Type a number of a track to play.```\n"
                for i, track in enumerate(tracks, start=1):
                    msg += "%s. %s\n" % (i, clean_text(track["info"]["title"]))
                msg += "```"
                msg = await ctx.send(msg)

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author

                try:
                    x = await self.bot.wait_for("message", check=check, timeout=10.0)
                except:
                    try:
                        await msg.edit(content="Timed out")
                    except:
                        pass
                    return

                try:
                    x = int(x.content)
                except:
                    return await ctx.send("Not a valid number, returning")
                if x not in list(range(1, len(tracks) + 1)):
                    return await ctx.send("Not a valid option, returning")

                track = tracks[x - 1]
                if track["info"]["length"] > 3600000:
                    return await ctx.send("Thats too long for me to play baka")

                await ctx.send("Added **%s** to queue" % clean_text(track["info"]["title"]))
                player.add(requester=ctx.author.id, track=track)

            if not player.is_playing:
                await player.play()

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def listenmoe(self, ctx):

        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in any voice channel ;w;")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send("Missing permissions to connect or speak ;w;")
            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("Join my voice channel you baka")
            if player.is_playing:
                player.queue.clear()

        track = (await self.bot.lavalink.get_tracks("https://listen.moe/stream"))["tracks"][0]
        player.add(requester=ctx.author.id, track=track)
        await player.play()
        await ctx.send("Playing uwu")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def volume(self, ctx, amount: int):
        """Change the volume"""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("I'm not even playing anything")
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("Join my voice channel you baka")

        amount = max(min(amount, 150), 0)

        await player.set_volume(amount)
        await ctx.send("Changed volume to %s" % player.volume)

    @commands.command(aliases=["stop"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def disconnect(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("I'm not connected to your vc ;w;")

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send("You're not in my voice channel >_<")

        player.queue.clear()
        await player.disconnect()
        await ctx.send("baibai")

    @commands.command(aliases=["playing"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        """Check whats currently playing"""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        em = discord.Embed(color=0xDEADBF)
        em.title = "Currently Playing"

        desc = ""
        if player.current:
            em.set_thumbnail(url=player.current.thumbnail)
            desc += "🔊 **%s**\n" % clean_text(player.current.title)
        for i, song in enumerate(player.queue):
            i += 1
            if i > 10:
                break
            desc += "%s. **%s**\n" % (i, clean_text(song.title))
        if desc == "":
            desc += "🔉 Nothing..."

        em.description = desc
        em.set_footer(text="%s in queue" % (len(player.queue),))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def skip(self, ctx):
        """Skip a song"""
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("I'm not playing anything")

        if not ctx.author.voice or ctx.author.voice.channel.id != int(player.channel_id):
            return await ctx.send("You're not in my voice channel >_<")

        await ctx.send("Skipped **%s**" % clean_text(player.current.title))
        await player.skip()

    @commands.group(aliases=["playlists"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def playlist(self, ctx):
        if not await r.table("playlists").get(str(ctx.author.id)).run(self.bot.r_conn):
            await r.table("playlists").insert({
                "id": str(ctx.author.id),
                "playlists": {}
            }).run(self.bot.r_conn)
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @playlist.command(name="add")
    async def playlist_add(self, ctx, playlist_name, *, song):
        """Add songs to one of your playlists"""
        playlists = (await r.table("playlists").get(str(ctx.author.id)).run(self.bot.r_conn))["playlists"]
        playlist = playlists.get(playlist_name, [])
        if len(playlist) > 15:
            return await ctx.send("You have too much tracks already in this playlist you baka")
        if not playlist:
            if (len(playlists) + 1) > 10:
                return await ctx.send("You have too much playlists already")
        await ctx.trigger_typing()

        if not url_rx.match(song):
            song = "ytsearch:" + song

        results = await self.bot.lavalink.get_tracks(song)

        if not results or not results["tracks"]:
            return await ctx.send("I found nothing ;w;")

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            if len(tracks) > 15:
                return await ctx.send("Too much tracks in this playlist ;w;")
            elif (len(tracks) + len(playlist)) > 15:
                return await ctx.send("Too much in queue already ;w;")

            for track in tracks:
                if not track["info"]["length"] > 3600000:
                    playlist.append(track)

            await ctx.send("Added **%s** to the playlist" % clean_text(results["playlistInfo"]["name"]))
            await r.table("playlists").get(str(ctx.author.id)).update({"playlists": {playlist_name: playlist}}).run(
                self.bot.r_conn)
        else:
            if len(results["tracks"]) < 2:
                track = results["tracks"][0]
                if track["info"]["isStream"]:
                    return await ctx.send("I can't add streams to playlists")
                if track["info"]["length"] > 3600000:
                    return await ctx.send("That song is too long for me to play ;w;")
                await ctx.send("Added **%s** to playlist" % clean_text(track["info"]["title"]))
                playlist.append(track)
                await r.table("playlists").get(str(ctx.author.id)).update({"playlists": {playlist_name: playlist}}).run(
                    self.bot.r_conn)
            else:
                tracks = results["tracks"][:5]
                msg = "Type a number of a track to play.```\n"
                for i, track in enumerate(tracks, start=1):
                    msg += "%s. %s\n" % (i, clean_text(track["info"]["title"]))
                msg += "```"
                msg = await ctx.send(msg)

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author

                try:
                    x = await self.bot.wait_for("message", check=check, timeout=10.0)
                except:
                    try:
                        await msg.delete()
                    except:
                        pass
                    return await ctx.send("Timed out.")

                try:
                    x = int(x.content)
                except:
                    return await ctx.send("Not a valid number, returning")
                if x not in list(range(1, len(tracks) + 1)):
                    return await ctx.send("Not a valid option, returning")

                track = tracks[x - 1]

                if track["info"]["isStream"]:
                    return await ctx.send("I can't add streams to playlists")
                if track["info"]["length"] > 3600000:
                    return await ctx.send("That song is too long for me to play ;w;")

                await ctx.send("Added **%s** to playlist" % clean_text(track["info"]["title"]))
                playlist.append(track)
                await r.table("playlists").get(str(ctx.author.id)).update({"playlists": {playlist_name: playlist}}).run(
                    self.bot.r_conn)

    @playlist.command(name="play")
    async def playlist_play(self, ctx, playlist_name):
        """Add one of your playlists to the queue"""

        playlists = (await r.table("playlists").get(str(ctx.author.id)).run(self.bot.r_conn))["playlists"]
        if not playlists.get(playlist_name):
            return await ctx.send("You don't have a playlist with that name >~<")

        playlist = playlists.get(playlist_name)
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in any voice channel ;w;")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send("Missing permissions to connect or speak ;w;")
            player.store("channel", ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("Join my voice channel you baka")

        if len(player.queue) + len(playlist) > 50:
            return await ctx.send("You are too much songs in your queue you baka")

        for track in playlist:
            player.add(requester=ctx.author.id, track=track)

        await ctx.send("Added playlist to queue")

        if not player.is_playing:
            await player.play()

    @playlist.command(name="display", aliases=["show", "view"])
    async def playlist_display(self, ctx, playlist_name=None):
        """Display one of your playlists"""
        playlists = (await r.table("playlists").get(str(ctx.author.id)).run(self.bot.r_conn))["playlists"]
        if not playlists:
            return await ctx.send("You don't have any playlists")

        if playlist_name:
            if not playlists.get(playlist_name):
                return await ctx.send("You don't have a playlist with that name >~<")
            msg = "Your Playlists Tracks:\n"
            for i, track in enumerate(playlists.get(playlist_name), start=1):
                if url_rx.match(track["info"]["title"]):
                    pass
                if i > 15:
                    break
                msg += "**%s.** %s\n" % (i, clean_text(track["info"]["title"]))

            await ctx.send(msg)
        else:
            msg = "Your Playlists:\n"
            for i, playlist in enumerate(playlists, start=1):
                if url_rx.match(playlist):
                    pass
                msg += "**%s.** %s\n" % (i, clean_text(playlist))

            await ctx.send(msg)

    @playlist.command(name="remove")
    async def playlist_remove(self, ctx, playlist_name):
        """Remove a song from the playlist"""
        playlists = (await r.table("playlists").get(str(ctx.author.id)).run(self.bot.r_conn))["playlists"]
        playlist = playlists.get(playlist_name)
        if not playlist:
            return await ctx.send("You don't have a playlist with that name >~<")

        msg = "**Type the number of a song to remove:**```\n"
        for i, track in enumerate(playlist, start=1):
            msg += "%s. %s\n" % (i, clean_text(track["info"]["title"]))
        msg += "```"

        await ctx.send(msg)

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            x = await self.bot.wait_for("message", check=check, timeout=10.0)
        except:
            try:
                await msg.delete()
            except:
                pass
            return await ctx.send("Timed out.")

        try:
            x = int(x.content)
        except:
            return await ctx.send("Not a valid number, returning")
        if x not in list(range(1, len(playlist) + 1)):
            print(len(playlist))
            return await ctx.send("Not a valid option, returning")

        song = playlist[x - 1]
        new_playlist = []
        for track in playlist:
            if not track == song:
                new_playlist.append(track)

        await ctx.send("Removed from playlist")
        if new_playlist:
            await r.table("playlists").get(str(ctx.author.id)).update({"playlists": {playlist_name: new_playlist}}).run(
                self.bot.r_conn)
        else:
            await r.table("playlists").get(str(ctx.author.id)).update({"playlists": {playlist_name: r.literal()}}).run(
                self.bot.r_conn)

    @playlist.command(name="delete")
    async def playlist_delete(self, ctx, playlist_name):
        """Delete a playlist"""
        playlists = (await r.table("playlists").get(str(ctx.author.id)).run(self.bot.r_conn))["playlists"]
        if not playlists.get(playlist_name):
            return await ctx.send("You don't have a playlist with that name >~<")
        await r.table("playlists").get(str(ctx.author.id)).update({"playlists": {playlist_name: r.literal()}}).run(
            self.bot.r_conn)
        await ctx.send("Deleted playlist.")

def setup(bot):
    bot.add_cog(Audio(bot))
