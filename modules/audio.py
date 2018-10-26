from discord.ext import commands
import discord
import asyncio, aiohttp

import lavalink
import config
import logging, re
import gettext

import rethinkdb as r

log = logging.getLogger()
url_rx = re.compile("https?:\/\/(?:www\.)?.+")

ll_headers = {
    "Authorization": config.lavalink_token
}

class Audio:

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, "lavalink"):
            log.info("Loaded lavalink")
            self.bot.loop.create_task(self.__post_to_hook("Loaded lavalink"))
            lavalink.Client(bot=bot, host=config.lava_host, password=config.lava_pass, loop=bot.loop,
                            rest_port=2343, ws_port=2344)

        if not self.bot.lavalink.hooks:
            log.info("Registering hook")
            self.bot.loop.create_task(self.__post_to_hook("Registered hook"))
            self.bot.lavalink.register_hook(self._track_hook)

        self.lang = {}
        self.languages = ["tsundere", "weeb", "chinese"]
        for x in self.languages:
            self.lang[x] = gettext.translation("general", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

    async def __post_to_hook(self, message):
        async with aiohttp.ClientSession() as cs:
            await cs.post(config.lavalink_hook, json={
                "embeds": [{
                    "title": "Lavalonk - %s" % self.bot.instance,
                    "description": message,
                    "color": 0xDEADBF
                }]
            })

    def __unload(self):
        log.info("Unloading audio")
        self.bot.loop.create_task(self.__post_to_hook("Unloaded"))
        for guild_id, player in self.bot.lavalink.players:
            self.bot.loop.create_task(player.disconnect())
            player.cleanup()
        self.bot.lavalink.players.clear()
        self.bot.lavalink.unregister_hook(self._track_hook)
        self.bot.lavalink.hooks.clear()

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
        _ = await self._get_text(ctx)

        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send(_("You are not in any voice channel ;w;"))

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send(_("Missing permissions to connect or speak ;w;"))
            player.store("channel", ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send(_("Join my voice channel you baka"))

        if len(player.queue) > 50:
            return await ctx.send(_("You are too much songs in your queue you baka"))

        query = query.strip("<>")

        if not url_rx.match(query):
            query = "ytsearch:" + query
        elif "osu.ppy.sh/beatmapsets" in query or "hentaihaven.org/" in query:
            await ctx.trigger_typing()
            if "hentaihaven" in query and not ctx.channel.is_nsfw():
                return await ctx.send(_("This is not an nsfw channel hmph shouldn't be posting that here >:|"))
            data = {"url": query}
            async with aiohttp.ClientSession() as cs:
                async with cs.post("https://lava.nekobot.xyz/api", json=data, headers=ll_headers) as r:
                    res = await r.json()
            if not res["message"].startswith("http"):
                return await ctx.send(_("Failed to get data ;w;"))
            query = res["message"]

        results = await self.bot.lavalink.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send(_("I found nothing ;w;"))

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            if len(tracks) > 50:
                return await ctx.send(_("Too much tracks in this playlist ;w;"))
            elif (len(tracks) + len(player.queue)) > 50:
                return await ctx.send(_("Too much in queue already ;w;"))

            for track in tracks:
                if not track["info"]["length"] > 3600000:
                    player.add(requester=ctx.author.id, track=track)

            await ctx.send(_("Added playlist **%s**") % results["playlistInfo"]["name"].replace("@", "@\u200B"))
        else:
            if len(results["tracks"]) < 2:
                track = results["tracks"][0]
                if track["info"]["length"] > 3600000:
                    return await ctx.send("Thats too long for me to play baka")
                await ctx.send(_("Added **%s** to queue") % track["info"]["title"].replace("@", "@\u200B"))
                player.add(requester=ctx.author.id, track=track)
            else:
                tracks = results["tracks"][:5]
                msg = _("Type a number of a track to play.```\n")
                for i, track in enumerate(tracks, start=1):
                    msg += "%s. %s\n" % (i, track["info"]["title"].replace("@", "@\u200B"))
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
                    return await ctx.send(_("Not a valid number, returning"))
                if x not in range(1, len(tracks)):
                    return await ctx.send(_("Not a valid option, returning"))

                track = tracks[x - 1]
                if track["info"]["length"] > 3600000:
                    return await ctx.send("Thats too long for me to play baka")

                await ctx.send(_("Added **%s** to queue") % track["info"]["title"].replace("@", "@\u200B"))
                player.add(requester=ctx.author.id, track=track)

            if not player.is_playing:
                await player.play()

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def listenmoe(self, ctx):
        _ = await self._get_text(ctx)

        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send(_("You are not in any voice channel ;w;"))

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send(_("Missing permissions to connect or speak ;w;"))
            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send(_("Join my voice channel you baka"))
            if player.is_playing:
                player.queue.clear()

        track = (await self.bot.lavalink.get_tracks("https://listen.moe/stream"))["tracks"][0]
        player.add(requester=ctx.author.id, track=track)
        await player.play()
        await ctx.send(_("Playing uwu"))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def volume(self, ctx, amount: int):
        """Change the volume"""
        _ = await self._get_text(ctx)
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(_("I'm not even playing anything"))
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("Join my voice channel you baka")

        amount = max(min(amount, 150), 0)

        await player.set_volume(amount)
        await ctx.send(_("Changed volume to %s") % player.volume)

    @commands.command(aliases=["stop"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def disconnect(self, ctx):
        _ = await self._get_text(ctx)
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(_("I'm not connected to your vc ;w;"))

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send(_("You're not in my voice channel >_<"))

        player.queue.clear()
        await player.disconnect()
        await ctx.send(_("baibai"))

    @commands.command(aliases=["playing"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        """Check whats currently playing"""
        _ = await self._get_text(ctx)
        player = self.bot.lavalink.players.get(ctx.guild.id)

        em = discord.Embed(color=0xDEADBF)
        em.title = _("Currently Playing")

        desc = ""
        if player.current:
            em.set_thumbnail(url=player.current.thumbnail)
            desc += "🔊 **%s**\n" % player.current.title.replace("@", "@\u200B")
        for i, song in enumerate(player.queue):
            i += 1
            if i > 10:
                break
            desc += "%s. **%s**\n" % (i, song.title.replace("@", "@\u200B"))
        if desc == "":
            desc += "🔉" + _("Nothing...")

        em.description = desc
        em.set_footer(text=_("%s in queue") % (len(player.queue),))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def skip(self, ctx):
        """Skip a song"""
        _ = await self._get_text(ctx)
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(_("I'm not playing anything"))

        if not ctx.author.voice or ctx.author.voice.channel.id != int(player.channel_id):
            return await ctx.send(_("You're not in my voice channel >_<"))

        await ctx.send(_("Skipped **%s**") % player.current.title.replace("@", "@\u200B"))
        await player.skip()

def setup(bot):
    bot.add_cog(Audio(bot))
