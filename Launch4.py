import shardedBot

if __name__ == "__main__":
    instance = 3
    instances = 4
    shards = 84
    shard_ids = [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83]
    shardedBot.NekoBot(instance=instance, instances=instances, shard_count=shards, shard_ids=shard_ids, max_messages=101).run()
