import discord
from discord.ext import commands
import logging, sys, time, os
import traceback
from datetime import datetime
import config
import gettext
import aioredis
import aiohttp
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
            fetch_offline_members=False,
            max_messages=kwargs.get("max_messages", 105),
            help_attrs={"hidden": True}
        )
        self.instance = instance
        self.instances = instances
        self.pipe = pipe
        self.ipc_queue = ipc_queue
        self.__shard_counter = 0
        self.languages = ["tsundere", "weeb", "chinese"]
        self.lang = {}
        for x in self.languages:
            self.lang[x] = gettext.translation("errors", localedir="locale", languages=[x])

        async def _init_redis():
            self.redis = await aioredis.create_redis(address=("localhost", 6379), loop=self.loop)

        async def _init_rethink():
            r.set_loop_type("asyncio")
            self.r_conn = await r.connect(host="localhost",
                                          db="nekobot")

        self.loop.create_task(_init_rethink())
        self.loop.create_task(_init_redis())

        self.remove_command("help")

        for file in os.listdir("modules"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.load_extension(f"modules.{name}")
                except:
                    logger.warning("Failed to load {}.".format(name))
                    traceback.print_exc()

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

    async def _get_text(self, ctx):
        lang = await self.get_language(ctx)
        if lang:
            if lang in self.languages:
                return self.lang[lang].gettext
            else:
                return gettext.gettext
        else:
            return gettext.gettext

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

        logger.info("READY, Instance {}/{}, Shards {}".format(self.instance, self.instances, self.shard_count))

    def run(self, token = config.token):
        super().run(token)

    async def on_command_error(self, ctx, exception):

        error = getattr(exception, "original", exception)
        if isinstance(error, discord.NotFound):
            return
        elif isinstance(error, discord.Forbidden):
            return
        elif isinstance(error, discord.HTTPException) or isinstance(error, aiohttp.ClientConnectionError):
            return await ctx.send((await self._get_text(ctx))("Failed to get data."))
        if isinstance(exception, commands.NoPrivateMessage):
            return
        elif isinstance(exception, commands.DisabledCommand):
            return
        elif isinstance(exception, commands.CommandInvokeError):
            async with aiohttp.ClientSession() as cs:
                await cs.post(
                    f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}",
                    json={
                        "embeds": [
                            {
                                "title": f"Command: {ctx.command.qualified_name}, Instance: {self.instance}",
                                "description": f"```py\n{exception}\n```\n By `{ctx.author}` (`{ctx.author.id}`)",
                                "color": 16740159
                            }
                        ]
                    })
            em = discord.Embed(color=0xDEADBF,
                               title="Error",
                               description=f"Error in command {ctx.command.qualified_name}, "
                                           f"[Support Server](https://discord.gg/q98qeYN).\n`{exception}`")
            await ctx.send(embed=em)
            logger.warning('In {}:'.format(ctx.command.qualified_name))
            logger.warning('{}: {}'.format(exception.original.__class__.__name__, exception.original))
        elif isinstance(exception, commands.BadArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.MissingRequiredArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.CheckFailure):
            await ctx.send((await self._get_text(ctx))("You are not allowed to use that command."), delete_after=5)
        elif isinstance(exception, commands.CommandOnCooldown):
            await ctx.send((await self._get_text(ctx))("Command is on cooldown... {:.2f}s left").format(exception.retry_after), delete_after=5)
        elif isinstance(exception, commands.CommandNotFound):
            return
        else:
            return
