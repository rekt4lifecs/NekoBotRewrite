# Modified version of https://github.com/KawaiiBot/AIO_Launcher
# License https://github.com/KawaiiBot/AIO_Launcher/blob/master/LICENSE

import traceback, os, sys
import datetime
from collections import Counter
import aioredis, aiomysql

from discord.ext import commands
import discord, config

import logging

# BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
# RESET_SEQ = "\033[0m"
# COLOR_SEQ = "\033[1;%dm"
# BOLD_SEQ = "\033[1m"
# TIME_SEQ = COLOR_SEQ % (30 + MAGENTA)
# NAME_SEQ = COLOR_SEQ % (30 + CYAN)
# FORMAT = "[$TIME_SEQ%(asctime)-3s$RESET]" \
#          "[$NAME_SEQ$BOLD%(name)-2s$RESET]" \
#          "[%(levelname)-1s]" \
#          "[%(message)s]" \
#          "[($BOLD%(filename)s$RESET:%(lineno)d)]"
#
#
# def formatter_message(message: str, colored: bool = True):
#     if colored:
#         message = message.replace("$RESET", RESET_SEQ)
#         message = message.replace("$BOLD", BOLD_SEQ)
#         message = message.replace("$TIME_SEQ", TIME_SEQ)
#         message = message.replace("$NAME_SEQ", NAME_SEQ)
#         return message
#     else:
#         message = message.replace("$RESET", "")
#         message = message.replace("$BOLD", "")
#         return message
#
#
# class ColoredFormatter(logging.Formatter):
#     def __init__(self, msg, use_color=True):
#         logging.Formatter.__init__(self, msg)
#         self.use_color = use_color
#
#     def format(self, record):
#         level_name = record.levelname
#         if self.use_color and level_name in COLORS:
#             level_name_color = COLOR_SEQ % (30 + COLORS[level_name]) + level_name + RESET_SEQ
#             record.levelname = level_name_color
#         message = record.msg
#         if self.use_color and level_name in COLORS:
#             message_color = COLOR_SEQ % (30 + BLUE) + message + RESET_SEQ
#             record.msg = message_color
#         return logging.Formatter.format(self, record)
#
#
# class ColoredLogger(logging.Logger):
#     def __init__(self, name):
#         logging.Logger.__init__(self, name, logging.INFO)
#         return
#
#
# COLORS = {
#     'WARNING': YELLOW,
#     'INFO': BLUE,
#     'DEBUG': WHITE,
#     'CRITICAL': YELLOW,
#     'ERROR': RED
# }
#
# logger = logging.getLogger()
# color_format = formatter_message(FORMAT, True)
# logging.setLoggerClass(ColoredLogger)
# color_formatter = ColoredFormatter(color_format)
# console = logging.StreamHandler()
# file = logging.FileHandler(filename=f'logs/{datetime.datetime.utcnow()}.log', encoding='utf-8', mode='w')
# console.setFormatter(color_formatter)
# file.setFormatter(color_formatter)
# logger.addHandler(console)
# logger.addHandler(file)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormat = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
file = logging.FileHandler(filename=f'logs/{datetime.datetime.utcnow()}.log', encoding='utf-8', mode='w')
file.setFormatter(logFormat)
console = logging.StreamHandler()
console.setFormatter(logFormat)
logger.addHandler(console)
logger.addHandler(file)

def _prefix_callable(bot, msg):
    prefixes = ['n!', 'N!']
    return commands.when_mentioned_or(*prefixes)(bot, msg)


class Instance:

    def __init__(self, instance, shard_count, ids, pipe):
        self.pipe = pipe
        self.bot = commands.AutoShardedBot(command_prefix=_prefix_callable,
                                           description="NekoBot",
                                           pm_help=None,
                                           shard_count=shard_count,
                                           shard_ids=ids,
                                           status=discord.Status.dnd,
                                           activity=discord.Game(name="Restarting..."),
                                           fetch_offline_members=False,
                                           max_messages=2500,
                                           help_attrs={'hidden': True})
        self.bot.counter = Counter()
        self.bot.command_usage = Counter()
        self.bot.prefix = "n!"
        self.bot.instance = instance

        async def _init_redis():
            self.redis = await aioredis.create_redis(address=("localhost", 6379), loop=self.bot.loop)

        async def _init_sql():
            self.sql_conn = await aiomysql.create_pool(host='localhost', port=3306,
                                              user='root', password=config.dbpass,
                                              db='nekobot', loop=self.bot.loop, autocommit=True)

        self.bot.loop.create_task(_init_sql())
        self.bot.loop.create_task(_init_redis())

        self.bot.add_listener(self.on_command_error)
        self.bot.add_listener(self.on_command)
        self.bot.add_listener(self.on_message)
        self.bot.add_listener(self.on_ready)
        self.bot.add_listener(self.on_shard_ready)

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

    async def on_shard_ready(self, shard):
        logger.info(f"Shard {shard} ready.")

    async def on_command(self, ctx):
        self.bot.command_usage[str(ctx.command)] += 1

    async def on_message(self, message):
        self.bot.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.bot.process_commands(message)

    async def on_ready(self):
        logger.info("Ready!")
        logger.info("Ready OwO")
        logger.info(f"Shards: {self.bot.shard_count}")
        logger.info(f"Servers {len(self.bot.guilds)}")
        logger.info(f"Users {len(set(self.bot.get_all_members()))}")
        await self.bot.change_presence(status=discord.Status.idle)

        for file in os.listdir("modules"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.bot.load_extension(f"modules.{name}")
                    logger.info(f"Loaded {name}")
                except:
                    logger.warning("Failed to load {}.".format(name), file=sys.stderr)
                    traceback.print_exc()

        self.pipe.send(1)
        self.pipe.close()