import discord
import config
import os, sys
import importlib

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

        # self.run()

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        print(message)

    async def on_ready(self):
        print("READY")
        print(self.commands)

    def register_commands(self):
        for file in os.listdir("modules"):
            if file.endswith(".py"):
                file = file.replace(".py", "")
                lib = importlib.import_module("modules.{}".format(file))
                if not hasattr(lib, "commands"):
                    del lib
                    del sys.modules["modules.{}".format(file)]
                    print("{} is missing commands var")
                else:
                    self.commands[file] = getattr(lib, "commands")

    def run(self, token: str = config.token):
        super().run(token)

if __name__ == "__main__":
    NekoBot(0, 1, 1, [0]).run(config.testtoken)
