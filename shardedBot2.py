import discord
from discord.ext import commands
import logging, sys, time
import aioredis
import rethinkdb as r
from datetime import datetime
import config

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
    file = logging.FileHandler(filename=f"logs/{str(time.time())}.log", encoding="utf-8", mode="w")
    file.setFormatter(color_formatter)
    logger.addHandler(file)

async def _prefix_callable(bot, msg):
    prefix = await bot.redis.get(f"{msg.author.id}-prefix")
    if not prefix:
        prefix = ["n!", "N!"]
    else:
        prefix = [prefix.decode("utf8"), "n!", "N!"]
    return commands.when_mentioned_or(*prefix)(bot, msg)

class NekoBot(commands.AutoShardedBot):

    def __init__(self, instance, instances, shard_count, shard_ids, pipe, ipc_queue, **kwargs):
        super().__init__(
            command_prefix=_prefix_callable,
            description="NekoBot",
            pm_help=None,
            shard_ids=shard_ids,
            shard_count=shard_count,
            status=discord.Status.idle,
            fetch_offline_members=False,
            max_messages=kwargs.get("max_messages", 105),
            help_attrs={"hidden": True}
        )
        self.instance = instance
        self.instances = instances
        self.pipe = pipe
        self.ipc_queue = ipc_queue
        self.__shard_counter = 0

        async def _init_redis():
            self.redis = await aioredis.create_redis(address=("localhost", 6379), loop=self.loop)

        async def _init_rethink():
            r.set_loop_type("asyncio")
            self.r_conn = await r.connect(host="localhost",
                                          db="nekobot")

        self.loop.create_task(_init_rethink())
        self.loop.create_task(_init_redis())

        self.remove_command("help")

        self.run()

    async def get_language(self, ctx):
        data = await self.redis.get("%s-lang" % ctx.author.id)
        if not data:
            return None
        dec = data.decode("utf8")
        if dec == "english":
            await self.redis.delete("%s-lang" % ctx.author.id)
            return None
        return dec

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

    async def on_command(self, ctx):
        logger.info("{} executed {}".format(ctx.author.id, ctx.command.name))

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
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_socket_response(self, msg):
        if not self.pipe.closed:
            if msg.get("t") == "READY":
                self.__shard_counter += 1
                if self.__shard_counter >= len(self.shard_ids):
                    del self.__shard_counter
                    self.pipe.send(1)
                    self.pipe.close()

    async def close(self):
        self.r_conn.close()
        self.redis.close()
        await super().close()

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = datetime.utcnow()

        logger.info("READY, Instance {}/{}, Shards {}".format(self.instance, len(self.instances), self.shard_count))

    def run(self):
        super().run(config.token)
