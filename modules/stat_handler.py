import asyncio, config, aiohttp
import logging

from .utils import instance_tools

log = logging.getLogger()

class StatHandler:

    def __init__(self, bot):
        self.bot = bot
        self.has_started = 0

    async def postloop(self):
        if not self.has_started == 1:
            self.has_started = 1
            while self.has_started:
                log.info("Getting all servers.")
                log.info("Attempting to update server count.")

                i = instance_tools.InstanceTools(self.bot.instances, self.bot.redis)
                guilds = await i.get_all_guilds()

                log.info("Servers: %s" % guilds)
                if self.bot.instance == 0:

                    async with aiohttp.ClientSession() as cs:
                        x = await cs.post(
                            "https://discordbots.org/api/bots/310039170792030211/stats",
                            json={
                                "server_count": int(guilds),
                                "shard_count": self.bot.shard_count
                            },
                            headers={
                                "Authorization": config.dbots_key
                            }
                        )
                        log.info("Posted to discordbots.org, {}".format(await x.json()))
                        x = await cs.post(
                            "https://discord.bots.gg/api/v1/bots/310039170792030211/stats",
                            json={
                                "guildCount": int(guilds),
                                "shardCount": self.bot.shard_count
                            },
                            headers={
                                "Authorization": config.dpw_key
                            }
                        )
                        log.info("Posted to discord.bots.gg, {}".format(await x.json()))
                        await cs.post(
                            "https://discord.services/api/bots/310039170792030211",
                            json={
                                "guild_count": int(guilds)
                            },
                            headers={
                                "Authorization": config.ds_key
                            }
                        )
                        log.info("Posted to discord.services, {}".format(await x.json()))
                        await cs.post(
                            "https://lbots.org/api/v1/bots/310039170792030211/stats",
                            json={
                                "guild_count": int(guilds),
                                "shard_count": self.bot.shard_count
                            },
                            headers={
                                "Authorization": config.lbots_key
                            }
                        )
                        log.info("Posted to lbots.org, {}".format(await x.json()))

                await asyncio.sleep(1800)

    async def on_ready(self):
        self.bot.loop.create_task(self.postloop())

def setup(bot):
    bot.add_cog(StatHandler(bot))
