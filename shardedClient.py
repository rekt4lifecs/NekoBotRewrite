import discord
import config
import os, sys
import importlib
import models
import aioredis
import re

arg_re = re.compile("\s+")

class NekoBot(discord.AutoShardedClient):

    def __init__(self, instance, instances, shard_count, shard_ids, **kwargs):
        super().__init__(
            shard_ids=shard_ids,
            shard_count=shard_count,
            fetch_offline_members=False,
            max_messages=kwargs.get("max_messages", 105)
        )

        self.instance = instance
        self.instances = instances

        self.commands = {}
        self.register_commands()

        print(self.commands)

        self.redis = None

        # self.run()

    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.content:
            return
        for prefix in await self.get_prefix(message.author.id):
            if message.content.startswith(prefix):
                return await self.process_message(message, prefix)

    async def process_message(self, message: discord.Message, prefix: str):
        message.content = message.content[len(prefix):]
        args = arg_re.split(message.content)
        if args[0] in self.get_all_commands():
            return await self.get_command(args[0]).invoke(models.Context(self, message), args)

    async def on_ready(self):
        print("READY, Instance {}/{}, Shards {}, Commands {}".format(
            self.instance + 1,
            self.instances,
            self.shard_count,
            len(self.get_all_commands())
        ))

    def register_commands(self):
        for file in os.listdir("modules"):
            if file.endswith(".py"):
                file = file.replace(".py", "")
                self.load_extension(file)

    def get_all_commands(self):
        cmds = list()
        for category in self.commands:
            for cmd in self.commands[category]:
                cmds.append(cmd.name)
        return cmds

    def get_command(self, command):
        for category in self.commands:
            for cmd in self.commands[category]:
                if cmd.name == command:
                    return cmd

    def load_extension(self, name):
        if name in list(self.commands):
            return
        lib = importlib.import_module("modules.{}".format(name))
        if not hasattr(lib, "commands"):
            del lib
            del sys.modules["modules.{}".format(name)]
            print("{} is missing commands var")
        else:
            self.commands[name] = [models.Command(x) if not isinstance(x, models.Command) else x for x in getattr(lib, "commands")]
            print("Loaded {}".format(name))

    def unload_extension(self, name):
        lib = self.commands.get(name)
        if lib is None:
            return
        del self.commands[name]
        del sys.modules["modules.{}".format(name)]

    async def get_prefix(self, u_id: int):
        data = await self.redis.get("{}-prefix".format(u_id))
        if data is None:
            return ["n!", "N!"]
        return ["n!", "N!", data.decode("utf8")]

    async def setup_connections(self):
        self.redis = await aioredis.create_redis(address=("localhost", 6379), loop=self.loop)

    def run(self, token: str = config.token):
        self.loop.create_task(self.setup_connections())
        super().run(token)

if __name__ == "__main__":
    NekoBot(0, 1, 1, [0]).run(config.testtoken)
