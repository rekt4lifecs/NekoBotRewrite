from discord.ext import commands
import discord
import config
import logging
import sys, time, os
import rethinkdb as r
import aioredis
import aiohttp
import asyncio
from datetime import datetime
from queue import Empty as EmptyQueue
import json
from modules.utils import instance_tools
import cProfile

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

def justrunpls(instance, instances, shard_count, shard_ids, pipe, ipc_queue):
    _globals = globals()
    _locals = locals()
    _globals["NekoBot"] = NekoBot
    cProfile.runctx("NekoBot(instance, instances, shard_count, shard_ids, pipe, ipc_queue).run()", globals=_globals, locals=_locals, filename="profile:{}:{}".format(int(time.time()), instance))

class NekoBot(commands.AutoShardedBot):

    def __init__(self, instance, instances, shard_count, shard_ids, pipe, ipc_queue, **kwargs):
        super().__init__(
            command_prefix=_prefix_callable,
            description="NekoBot",
            pm_help=None,
            shard_ids=shard_ids,
            shard_count=shard_count,
            status=discord.Status.idle,
            game=discord.Game("tests"),
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
            self.r_conn = await r.connect(host="localhost", db="nekobot")

        self.loop.create_task(_init_rethink())
        self.loop.create_task(_init_redis())

        self.remove_command("help")

        for module in os.listdir("modules"):
            if module.endswith(".py"):
                try:
                    self.load_extension("modules.{}".format(module[:-3]))
                    logger.info("Loaded {}".format(module))
                except Exception as e:
                    logger.error("Failed to load {}, {}".format(module, e))

        self.loop.create_task(self.start_loop())

    async def start_loop(self):
        while True:
            try:
                data = self.ipc_queue.get_nowait()
                if data:
                    data = json.loads(data)
                    if data["op"] == "reload":
                        self.unload_extension("modules.{}".format(data["d"]))
                        self.load_extension("modules.{}".format(data["d"]))
                        logger.info("Reloaded {}".format(data["d"]))
                    elif data["op"] == "load":
                        self.load_extension("modules.{}".format(data["d"]))
                        logger.info("Loaded {}".format(data["d"]))
                    elif data["op"] == "unload":
                        self.unload_extension("modules.{}".format(data["d"]))
                        logger.info("Unloaded {}".format(data["d"]))
            except EmptyQueue:
                pass
            except Exception as e:
                logger.error("IPC Failed, {}".format(e))
            try:
                await self.redis.set("instance%s-guilds" % self.instance, len(self.guilds))
                await self.redis.set("instance%s-users" % self.instance, sum([x.member_count for x in self.guilds]))
                await self.redis.set("instance%s-channels" % self.instance, len(set(self.get_all_channels())))
            except:
                logger.error("Redis update failed")
            try:
                await self.post_stats()
            except:
                logger.error("Failed to post stats")
            await asyncio.sleep(240)

    async def post_stats(self):
        if self.instance == 0:
            i = instance_tools.InstanceTools(self.instances, self.redis)
            async with aiohttp.ClientSession() as cs:
                await cs.post("https://www.carbonitex.net/discord/data/botdata.php", json={
                    "key": config.carbon,
                    "servercount": await i.get_all_guilds()
                })

    async def on_socket_response(self, msg):
        if not self.pipe.closed:
            if msg.get("t") == "READY":
                self.__shard_counter += 1
                if self.__shard_counter >= len(self.shard_ids):
                    del self.__shard_counter
                    self.pipe.send(1)
                    self.pipe.close()

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = datetime.utcnow()
        async with aiohttp.ClientSession() as cs:
            await cs.post(config.status_smh, json={
                "content": "instance {} ready smh".format(self.instance)
            })
        logger.info("READY")
        if not self.pipe.closed:
            self.pipe.send(1)
            self.pipe.close()

    async def on_command(self, ctx):
        logger.info("{} executed {}".format(ctx.author.id, ctx.command.name))

    async def send_cmd_help(self, ctx):
        return await ctx.send_help(ctx.command)

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        self.r_conn.close()
        self.redis.close()
        await super().close()

    def run(self, token: str = config.token):
        super().run(token)

    async def on_command_error(self, ctx, exception):
        error = getattr(exception, "original", exception)
        if isinstance(error, discord.NotFound):
            return
        elif isinstance(error, discord.Forbidden):
            return
        elif isinstance(error, discord.HTTPException) or isinstance(error, aiohttp.ClientConnectionError):
            return await ctx.send("Failed to get data.")
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
            await ctx.send("You are not allowed to use that command.", delete_after=5)
        elif isinstance(exception, commands.CommandOnCooldown):
            await ctx.send("Command is on cooldown... {:.2f}s left".format(exception.retry_after), delete_after=5)
        elif isinstance(exception, commands.CommandNotFound):
            return
        return

if __name__ == "__main__":
    NekoBot(0, 1, 1, [0], None).run(config.testtoken)
