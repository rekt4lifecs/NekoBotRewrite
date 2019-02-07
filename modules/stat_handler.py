import asyncio, config, aiohttp
import logging

from .utils import instance_tools

log = logging.getLogger()

statuses = ["OwO whats n!help", "🤔🤔🤔", "👀", "(╯°□°）╯︵ ┻━┻",
          "¯\_(ツ)_/¯", "┬─┬ノ(ಠ_ಠノ)", "><(((('>", "_/\__/\__0>", "ô¿ô", "°º¤ø,¸¸,ø¤º°`°º¤ø,", "=^..^=",
          "龴ↀ◡ↀ龴", "^⨀ᴥ⨀^", "^⨀ᴥ⨀^", "⨌⨀_⨀⨌", "•|龴◡龴|•", "ˁ˚ᴥ˚ˀ", "⦿⽘⦿", " (╯︵╰,)",
          " (╯_╰)", "㋡", "ˁ˚ᴥ˚ˀ", "\(^-^)/", "uwu", ":lurk:", "b-baka >_<",
          "I-it's not like I like you or anything!", "ばか >_<", "(//・.・//)", "....T-Thanks.....",
          "Hmph"]

class StatHandler:

    def __init__(self, bot):
        self.bot = bot
        self.has_started = 0
        self.token = config.dbots_key

    async def postloop(self):
        if not self.has_started == 1:
            self.has_started = 1
            while True:
                log.info("Getting all servers.")
                log.info("Attempting to update server count.")

                i = instance_tools.InstanceTools(self.bot.instances, self.bot.redis)
                guilds = await i.get_all_guilds()

                # game = discord.Streaming(name=random.choice(statuses), url="https://www.twitch.tv/nekoboat")
                # await self.bot.change_presence(activity=game)
                log.info("Servers: %s" % guilds)
                if self.bot.instance == 0:

                    async with aiohttp.ClientSession() as cs:
                        await cs.post(
                            "https://discordbots.org/api/bots/310039170792030211/stats",
                            json={
                                "server_count": int(guilds),
                                "shard_count": self.bot.shard_count
                            },
                            headers={
                                "Authorization": config.dbots_key
                            }
                        )
                        await cs.post(
                            "https://discord.bots.gg/api/v1/bots/310039170792030211/stats",
                            json={
                                "guildCount": int(guilds),
                                "shardCount": self.bot.shard_count
                            },
                            headers={
                                "Authorization": config.dpw_key
                            }
                        )
                        await cs.post(
                            "https://discord.services/api/bots/310039170792030211",
                            json={
                                "guild_count": int(guilds)
                            },
                            headers={
                                "Authorization": config.ds_key
                            }
                        )

                await asyncio.sleep(1800)

    # async def on_ready(self):
    #     await self.postloop()

def setup(bot):
    bot.add_cog(StatHandler(bot))
