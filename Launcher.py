import shardedBot
from multiprocessing import Process, Pipe
import asyncio
import shutil

shards = 112
shards_per_instance = 16
instances = int(shards / shards_per_instance)

def wait(delay: int):
    loop.run_until_complete(asyncio.sleep(delay))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    executable = str(shutil.which("python3.6") or shutil.which("py")).split("/")[-1]
    queue = list()
    for i in range(0, instances):
        start = i * shards_per_instance
        last = min(start + shards_per_instance, shards)
        ids = list(range(start, last))
        queue.append([i, ids])

    for instance, shard_ids in queue:
        print("Launching Instance {}".format(instance))
        listen, send = Pipe()
        p = Process(target=shardedBot.NekoBot, args=(instance, instances, shards, shard_ids, send,))
        p.start()

        if listen.recv() == 1:
            print("Instance {} Launched".format(instance))
        listen.close()
