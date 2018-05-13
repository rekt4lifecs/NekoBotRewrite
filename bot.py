from discord.ext import commands
import logging, traceback, sys, discord
from datetime import date
from collections import Counter
import datetime
import aiohttp, asyncio, aioredis
import random
import config

log = logging.getLogger('NekoBot')
log.setLevel(logging.INFO)
date = f"{date.today().timetuple()[0]}_{date.today().timetuple()[1]}_{date.today().timetuple()[2]}"
handler = logging.FileHandler(filename=f'NekoBot_{date}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

startup_extensions = {
    'modules.audio',
    'modules.cardgame',
    'modules.chatbot',
    'modules.discordbots',
    'modules.donator',
    'modules.eco',
    'modules.fun',
    'modules.games',
    'modules.general',
    'modules.imgwelcome',
    'modules.marriage',
    'modules.mod',
    'modules.nsfw',
    'modules.reactions',
    'modules.error_handler'
}

def _prefix_callable(bot, msg):
    prefixes = ['n!', 'N!']
    return commands.when_mentioned_or(*prefixes)(bot, msg)

class NekoBot(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, #commands.when_mentioned_or('n!')
                         description="NekoBot",
                         pm_help=None,
                         shard_id=0,
                         status=discord.Status.dnd,
                         max_messages=5000,
                         help_attrs={'hidden': True})
        self.counter = Counter()

        async def _init_redis():
            self.redis = await aioredis.create_redis(address=("localhost", 6379), loop=self.loop)

        self.loop.create_task(_init_redis())

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except:
                print("Failed to load {}.".format(extension), file=sys.stderr)
                traceback.print_exc()

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.close()

    async def on_shard_ready(self, shard_id):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(f"Shard {shard_id} Connected...")
        webhook_url = f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}"
        payload = {
            "embeds": [
                {
                    "title": "Shard Connect.",
                    "description": f"Shard {shard_id} has connected.",
                    "color": 14593471
                }
            ]
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.post(webhook_url, json=payload) as r:
                res = await r.read()
                print(res)

    async def on_ready(self):
        async with aiohttp.ClientSession() as cs:
            async with cs.post("http://localhost:1212",
                               json={"instance": 0,
                                     "servers": len(self.guilds)}) as r:
                res = await r.json()
                print(res)
        print("             _         _           _   \n"
              "            | |       | |         | |  \n"
              "  _ __   ___| | _____ | |__   ___ | |_ \n"
              " | '_ \ / _ \ |/ / _ \| '_ \ / _ \| __|\n"
              " | | | |  __/   < (_) | |_) | (_) | |_ \n"
              " |_| |_|\___|_|\_\___/|_.__/ \___/ \__|\n"
              "                                       \n"
              "                                       ")
        print("Ready OwO")
        print(f"Shards: {self.shard_count}")
        print(f"Servers {len(self.guilds)}")
        print(f"Users {len(set(self.get_all_members()))}")
        await self.change_presence(status=discord.Status.idle)
        
    def run(self):
        super().run(config.token)

def run_bot():
    bot = NekoBot()
    bot.run()

if __name__ == '__main__':
    run_bot()
