from discord.ext import commands
import logging, traceback, sys, discord
from datetime import date
from collections import Counter
import datetime
import aiohttp, aioredis, aiomysql
import os
import config

log = logging.getLogger('NekoBot')
log.setLevel(logging.INFO)
date = f"{date.today().timetuple()[0]}_{date.today().timetuple()[1]}_{date.today().timetuple()[2]}"
handler = logging.FileHandler(filename=f'NekoBot_{date}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
                         fetch_offline_members=False,
                         max_messages=2500,
                         help_attrs={'hidden': True})
        self.counter = Counter()
        self.command_usage = Counter()

        async def _init_redis():
            self.redis = await aioredis.create_redis(address=("localhost", 6379), loop=self.loop)

        async def _init_sql():
            self.sql_conn = await aiomysql.create_pool(host='localhost', port=3306,
                                              user='root', password=config.dbpass,
                                              db='nekobot', loop=self.loop, autocommit=True)

        self.loop.create_task(_init_sql())
        self.loop.create_task(_init_redis())

        for file in os.listdir("modules"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.load_extension(f"modules.{name}")
                except:
                    print(bcolors.FAIL + "Failed to load {}.".format(name) + bcolors.ENDC, file=sys.stderr)
                    traceback.print_exc()

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

    async def on_command(self, ctx):
        self.command_usage[str(ctx.command)] += 1

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    # async def on_error(self, event_method, *args, **kwargs):
    #     print(bcolors.FAIL + "[ERROR]" + bcolors.ENDC)
    #     sys.exc_info()

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        print(bcolors.FAIL + "[CLOSING]" + bcolors.ENDC)
        await super().close()
        await self.close()

    async def on_shard_ready(self, shard_id):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(bcolors.OKBLUE + f"Shard {shard_id} Connected..." + bcolors.ENDC)
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
        print(bcolors.HEADER + "             _         _           _   \n"
              "            | |       | |         | |  \n"
              "  _ __   ___| | _____ | |__   ___ | |_ \n"
              " | '_ \ / _ \ |/ / _ \| '_ \ / _ \| __|\n"
              " | | | |  __/   < (_) | |_) | (_) | |_ \n"
              " |_| |_|\___|_|\_\___/|_.__/ \___/ \__|\n"
              "                                       \n"
              "                                       " + bcolors.ENDC)
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
