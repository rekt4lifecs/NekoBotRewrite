import shardedBot

if __name__ == "__main__":
    instance = 2
    instances = 4
    shards = 78
    shard_ids = [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]
    shardedBot.NekoBot(instance=instance, instances=instances, shard_count=shards, shard_ids=shard_ids, max_messages=105).run()
