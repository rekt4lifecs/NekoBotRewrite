import discord
import logging
import datetime
import sys
from multiprocessing import Queue
from config import token

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
    file = logging.FileHandler(filename=f'logs/{datetime.datetime.utcnow()}-TEST.log',
                               encoding='utf-8',
                               mode='w')
    file.setFormatter(color_formatter)
    logger.addHandler(file)

class NekoBot(discord.AutoShardedClient):

    def __init__(self, instance, instances, shard_count, shard_ids, pipe, ipc_queue: Queue, **kwargs):
        super().__init__(
            max_messages=101,
            shard_ids=shard_ids,
            shard_count=shard_count,
            status=discord.Status.invisible,
            fetch_offline_members=False
        )
        self.instance = instance
        self.instances = instances
        self.pipe = pipe
        self.ipc_queue = ipc_queue
        self.shard_ids = shard_ids
        self.__shard_counter = 0

        super().run(token)

    async def on_socket_response(self, msg):
        event = msg.get("t")

        if not self.pipe.closed:
            if event == "READY":
                self.__shard_counter += 1
                if self.__shard_counter >= len(self.shard_ids):
                    del self.__shard_counter
                    self.pipe.send(1)
                    self.pipe.close()
