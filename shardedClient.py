import discord
import config

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

        # self.run()

    async def on_message(self, msg):
        pass

    async def on_ready(self):
        print("READY")

    def run(self, token: str = config.token):
        super().run(token)

if __name__ == "__main__":
    NekoBot(0, 1, 1, [0]).run(config.testtoken)
