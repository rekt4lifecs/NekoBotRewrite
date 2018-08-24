import asyncio, config, discord, random, aiohttp
import logging

from .utils import instance_tools

log = logging.getLogger()

stats2 = ["OwO whats n!help", "🤔🤔🤔", "👀", "(╯°□°）╯︵ ┻━┻",
                  "¯\_(ツ)_/¯", "┬─┬ノ(ಠ_ಠノ)", "><(((('>", "_/\__/\__0>", "ô¿ô", "°º¤ø,¸¸,ø¤º°`°º¤ø,", "=^..^=",
                  "龴ↀ◡ↀ龴", "^⨀ᴥ⨀^", "^⨀ᴥ⨀^", "⨌⨀_⨀⨌", "•|龴◡龴|•", "ˁ˚ᴥ˚ˀ", "⦿⽘⦿", " (╯︵╰,)",
                  " (╯_╰)", "㋡", "ˁ˚ᴥ˚ˀ", "\(^-^)/", "uwu", ":lurk:"]

class DiscordBotsOrgAPI:
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot):
        self.bot = bot
        self.has_started = 0
        self.token = config.dbots_key

    async def startdbl(self):
        if not self.has_started == 1:
            self.has_started = 1
            while True:
                log.info("Getting all servers.")
                log.info("Attempting to update server count.")

                i = instance_tools.InstanceTools(self.bot.instances, self.bot.redis)
                guilds = await i.get_all_guilds()

                game = discord.Streaming(name=random.choice(stats2), url="https://www.twitch.tv/nekoboat")
                await self.bot.change_presence(activity=game)
                log.info("Servers: %s" % guilds)
                if self.bot.instance == 0:
                    try:
                        url = "https://discordbots.org/api/bots/310039170792030211/stats"
                        payload = {
                            "server_count": int(guilds),
                            "shard_count": self.bot.shard_count
                        }
                        async with aiohttp.ClientSession() as cs:
                            await cs.post(url, json=payload, headers={"Authorization": config.dbots_key})
                        log.info("Posted server count. {}".format(guilds))
                    except Exception as e:
                        log.error('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

                    try:
                        async with aiohttp.ClientSession() as session:
                            await session.post('https://bots.discord.pw/api/bots/310039170792030211/stats',
                                                    headers={'Authorization': f'{config.dpw_key}'},
                                                    json={"server_count": int(guilds),
                                                          "shard_count": self.bot.shard_count})
                    except Exception as e:
                        log.error(f"Failed to post to pw, {e}")
                    try:
                        url = "https://discord.services/api/bots/310039170792030211"
                        payload = {
                            "guild_count": int(guilds)
                        }
                        async with aiohttp.ClientSession() as cs:
                            await cs.post(url, json=payload, headers={"Authorization": config.ds_key})
                    except Exception as e:
                        log.error(f"Failed to post to ds, {e}")
                # try:
                #     url = f"https://listcord.com/api/bot/{self.bot.user.id}/guilds"
                #     async with aiohttp.ClientSession() as cs:
                #         await cs.post(url, headers={"Authorization": config.listcord}, json={"guilds": int(guilds)})
                # except Exception as e:
                #     log.error(f"Failed to post to listcord, {e}")
                await asyncio.sleep(1800)

    async def on_ready(self):
        await self.startdbl()

def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
