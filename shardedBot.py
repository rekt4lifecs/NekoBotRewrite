from discord.ext import commands
import logging, traceback, discord
from collections import Counter
import datetime
import asyncio, aioredis
import os, sys

import config
import rethinkdb as r

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
TIME_SEQ = COLOR_SEQ % (30 + MAGENTA)
NAME_SEQ = COLOR_SEQ % (30 + CYAN)
FORMAT = "[$TIME_SEQ%(asctime)-3s$RESET]" \
         "[$NAME_SEQ$BOLD%(name)-2s$RESET]" \
         "[%(levelname)-1s]" \
         "[%(message)s]" \
         "[($BOLD%(filename)s$RESET:%(lineno)d)]"


def formatter_message(message: str, colored: bool = True):
    if colored:
        message = message.replace("$RESET", RESET_SEQ)
        message = message.replace("$BOLD", BOLD_SEQ)
        message = message.replace("$TIME_SEQ", TIME_SEQ)
        message = message.replace("$NAME_SEQ", NAME_SEQ)
        return message
    else:
        message = message.replace("$RESET", "")
        message = message.replace("$BOLD", "")
        return message


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        level_name = record.levelname
        if self.use_color and level_name in COLORS:
            level_name_color = COLOR_SEQ % (30 + COLORS[level_name]) + level_name + RESET_SEQ
            record.levelname = level_name_color
        message = record.msg
        if self.use_color and level_name in COLORS:
            message_color = COLOR_SEQ % (30 + BLUE) + message + RESET_SEQ
            record.msg = message_color
        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.INFO)
        return


COLORS = {
    'WARNING': YELLOW,
    'INFO': BLUE,
    'DEBUG': WHITE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}

logger = logging.getLogger()
logger.setLevel(logging.INFO)
color_format = formatter_message(FORMAT, True)
logging.setLoggerClass(ColoredLogger)
color_formatter = ColoredFormatter(color_format)
console = logging.StreamHandler()
console.setFormatter(color_formatter)
logger.addHandler(console)

if sys.platform == "linux":
    file = logging.FileHandler(filename=f'logs/{datetime.datetime.utcnow()}.log', encoding='utf-8', mode='w')
    file.setFormatter(color_formatter)
    logger.addHandler(file)

async def _prefix_callable(bot, msg):
    prefix = await bot.redis.get(f"{msg.author.id}-prefix")
    if not prefix:
        prefix = ['n!', 'N!']
    else:
        prefix = [prefix.decode("utf8"), "n!", "N!"]
    return commands.when_mentioned_or(*prefix)(bot, msg)

class NekoBot(commands.AutoShardedBot):

    def __init__(self, instance, instances, shard_count, shard_ids, **kwargs):
        super().__init__(command_prefix=_prefix_callable,
                         description="NekoBot",
                         pm_help=None,
                         shard_ids=shard_ids,
                         shard_count=shard_count,
                         status=discord.Status.dnd,
                         activity=discord.Game(name="Restarting..."),
                         fetch_offline_members=False,
                         max_messages=kwargs.get("max_messages", 105),
                         help_attrs={'hidden': True})
        self.counter = Counter()
        self.command_usage = Counter()
        self.instance = instance
        self.instances = instances

        async def _init_redis():
            self.redis = await aioredis.create_redis(address=("localhost", 6379), loop=self.loop)

        async def _init_rethink():
            r.set_loop_type("asyncio")
            self.r_conn = await r.connect(host="localhost",
                                          db="nekobot")

        self.loop.create_task(_init_rethink())
        self.loop.create_task(_init_redis())

        for file in os.listdir("modules"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.load_extension(f"modules.{name}")
                except:
                    logger.warning("Failed to load {}.".format(name))
                    traceback.print_exc()
    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

    async def on_command(self, ctx):
        self.counter["commands_used"] += 1
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

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        self.r_conn.close()
        self.redis.close()
        await super().close()

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print("             _         _           _   \n"
                               "            | |       | |         | |  \n"
                               "  _ __   ___| | _____ | |__   ___ | |_ \n"
                               " | '_ \ / _ \ |/ / _ \| '_ \ / _ \| __|\n"
                               " | | | |  __/   < (_) | |_) | (_) | |_ \n"
                               " |_| |_|\___|_|\_\___/|_.__/ \___/ \__|\n"
                               "                                       \n"
                               "                                       ")
        logger.info("Ready OwO")
        logger.info(f"Shards: {self.shard_count}")
        logger.info(f"Servers {len(self.guilds)}")
        logger.info(f"Instance {self.instance}")
        logger.info(f"Users {len(set(self.get_all_members()))}")
        await self.change_presence(status=discord.Status.idle)

        if not hasattr(self, "instancePoster"):
            self.instancePoster = True
            while self.instancePoster:
                await self.redis.set("instance%s-guilds" % self.instance, len(self.guilds))
                await self.redis.set("instance%s-users" % self.instance, len(set(self.get_all_members())))
                await self.redis.set("instance%s-messages" % self.instance, self.counter["messages_read"])
                await self.redis.set("instance%s-commands" % self.instance, self.counter["commands_used"])
                await self.redis.set("instance%s-channels" % self.instance, len(set(self.get_all_channels())))
                logger.info(f"Updated Instance {self.instance}'s Guild Count with {len(self.guilds)}")

                if self.instance == 0:

                    top_users = await r.table("economy").order_by(r.desc("balance")).limit(10).run(self.r_conn)

                    for i, u in enumerate(top_users):
                        try:
                            user = await self.get_user_info(int(u["id"]))
                            username = user.name + "#" + user.discriminator
                        except:
                            username = "Unknown User"

                        await self.redis.set("top%s" % i, username)

                await asyncio.sleep(300)

    def run(self):
        super().run(config.token)
