from discord.ext import commands
import logging, traceback, sys, discord
from collections import Counter
import datetime
import aioredis, aiomysql
import os
import config

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logFormat = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
# file = logging.FileHandler(filename=f'logs/{datetime.datetime.utcnow()}.log', encoding='utf-8', mode='w')
# file.setFormatter(logFormat)
# console = logging.StreamHandler()
# console.setFormatter(logFormat)
# logger.addHandler(console)
# logger.addHandler(file)

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
color_format = formatter_message(FORMAT, True)
logging.setLoggerClass(ColoredLogger)
color_formatter = ColoredFormatter(color_format)
console = logging.StreamHandler()
file = logging.FileHandler(filename=f'logs/{datetime.datetime.utcnow()}.log', encoding='utf-8', mode='w')
console.setFormatter(color_formatter)
file.setFormatter(color_formatter)
logger.addHandler(console)
logger.addHandler(file)

def _prefix_callable(bot, msg):
    prefixes = ['n!', 'N!']
    return commands.when_mentioned_or(*prefixes)(bot, msg)


class NekoBot(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix=_prefix_callable,  # commands.when_mentioned_or('n!')
                         description="NekoBot",
                         pm_help=None,
                         shard_ids=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                         shard_count=30,
                         status=discord.Status.dnd,
                         activity=discord.Game(name="Restarting..."),
                         fetch_offline_members=False,
                         max_messages=2500,
                         help_attrs={'hidden': True})
        self.counter = Counter()
        self.command_usage = Counter()
        self.instance = 0

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
                    logger.warning("Failed to load {}.".format(name), file=sys.stderr)
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

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.close()

    async def on_shard_ready(self, shard_id):
        logger.info(f"Shard {shard_id} connected.")

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
        logger.info(f"Users {len(set(self.get_all_members()))}")
        await self.change_presence(status=discord.Status.idle)

    def run(self):
        super().run(config.token)


def run_bot():
    bot = NekoBot()
    bot.run()


if __name__ == '__main__':
    run_bot()
