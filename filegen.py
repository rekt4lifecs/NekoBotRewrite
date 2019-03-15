template = """
import shardedBot2

class Pipe:
    closed = True

if __name__ == "__main__":
    shardedBot2.NekoBot({}, Pipe(), None)
"""

shards = 128
shards_per_instance = 16
instances = int(shards / shards_per_instance)
processes = list()

if __name__ == "__main__":
    queue = list()
    for i in range(0, instances):
        start = i * shards_per_instance
        last = min(start + shards_per_instance, shards)
        ids = list(range(start, last))
        queue.append([i, ids])

    for instance, shard_ids in queue:
        data = "{}, {}, {}, {}".format(instance, instances, shards, str(shard_ids))
        with open("Launch{}.py".format(instance), "w") as f:
            f.write(template.format(data))
