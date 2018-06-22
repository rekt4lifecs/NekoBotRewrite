import asyncio, config, discord, random, aiohttp
import logging

log = logging.getLogger()

messages = ["OwO Whats this", "MonkaS", "OwO", "Haiiiii", ".help", "🤔🤔🤔", "HMMM🤔", "USE n! WEW", "n!HELP REE"]
stats2 = ["OwO whats n!help", "🤔🤔🤔", "👀", "(╯°□°）╯︵ ┻━┻",
                  "¯\_(ツ)_/¯", "┬─┬ノ(ಠ_ಠノ)", "><(((('>", "_/\__/\__0>", "ô¿ô", "°º¤ø,¸¸,ø¤º°`°º¤ø,", "=^..^=",
                  "龴ↀ◡ↀ龴", "^⨀ᴥ⨀^", "^⨀ᴥ⨀^", "⨌⨀_⨀⨌", "•|龴◡龴|•", "ˁ˚ᴥ˚ˀ", "⦿⽘⦿", " (╯︵╰,)",
                  " (╯_╰)", "㋡", "ˁ˚ᴥ˚ˀ", "\(^-^)/"]

class DiscordBotsOrgAPI:
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = config.dbots_key

    async def startdbl(self):
        while True:
            log.info("Getting all servers.")
            log.info("Attempting to update server count.")
            instance1 = (await self.bot.redis.get("instance0-guilds")).decode("utf8")
            instance2 = (await self.bot.redis.get("instance1-guilds")).decode("utf8")
            servers = int(instance1) + int(instance2)
            game = discord.Streaming(name=random.choice(stats2), url="https://www.twitch.tv/rektdevlol")
            await self.bot.change_presence(activity=game)
            if self.bot.instance == 0:
                try:
                    url = "https://discordbots.org/api/bots/310039170792030211/stats"
                    payload = {
                        "server_count": int(servers),
                        "shard_count": self.bot.shard_count
                    }
                    async with aiohttp.ClientSession() as cs:
                        await cs.post(url, json=payload, headers={"Authorization": config.dbots_key})
                    log.info("Posted server count. {}".format(servers))
                except Exception as e:
                    log.error('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

                try:
                    async with aiohttp.ClientSession() as session:
                        await session.post('https://bots.discord.pw/api/bots/310039170792030211/stats',
                                                headers={'Authorization': f'{config.dpw_key}'},
                                                json={"server_count": int(servers),
                                                      "shard_count": self.bot.shard_count})
                except Exception as e:
                    log.error(f"Failed to post to pw, {e}")
                try:
                    url = "https://discord.services/api/bots/310039170792030211"
                    payload = {
                        "guild_count": int(servers)
                    }
                    async with aiohttp.ClientSession() as cs:
                        await cs.post(url, json=payload, headers={"Authorization": config.ds_key})
                except Exception as e:
                    log.error(f"Failed to post to ds, {e}")
            await asyncio.sleep(1800)

    async def on_ready(self):
        await self.startdbl()

def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
