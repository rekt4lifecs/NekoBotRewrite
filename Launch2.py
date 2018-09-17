import shardedBot

if __name__ == "__main__":
    instance = 1
    instances = 4
    shards = 92
    shard_ids = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
    shardedBot.NekoBot(instance=instance, instances=instances, shard_count=shards, shard_ids=shard_ids, max_messages=101).run()
