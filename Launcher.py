import shardedBot
from multiprocessing import Process, Pipe, Queue
import asyncio
import shutil
import os
from signal import SIGKILL

shards = 128
shards_per_instance = 16
instances = int(shards / shards_per_instance)
processes = list()

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

    ipc_queue = Queue()

    for instance, shard_ids in queue:
        listen, send = Pipe()
        p = Process(target=shardedBot.NekoBot, args=(instance, instances, shards, shard_ids, send, ipc_queue))
        p.start()
        print("Launching Instance {} (PID {})".format(instance, p.pid))
        processes.append(p.pid)

        if listen.recv() == 1:
            print("Instance {} Launched".format(instance))
        listen.close()

    try:
        while True:
            wait(5)
    except KeyboardInterrupt:
        for process in processes:
            os.kill(process, SIGKILL)
            print("Killed {}".format(process))
        print("Finished")
