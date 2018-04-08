import asyncio
import math
import os
import shutil
import subprocess
import sys
from multiprocessing import Process, Pipe

import instance


loop = asyncio.get_event_loop()
executable = str(shutil.which('python3.6') or shutil.which('py')).split('/')[-1]
instance_queue = []
instances = []


class PendingInstance:
    def __init__(self, i_id, total_shards, shard_ids):
        self.id = i_id
        self.total_shards = total_shards
        self.shard_ids = shard_ids


def launch_next_shard():
    if instance_queue:
        i = instance_queue.pop(0)
        print('Launching instance {}'.format(i.id))
        listen, send = Pipe()
        p = Process(target=instance.Instance, args=(i.id, i.total_shards, i.shard_ids, send,))
        instances.append(p)
        p.start()

        if listen.recv() == 1:
            launch_next_shard()
        listen.close()
    else:
        print('All instances launched!')


def wait(delay: int):
    loop.run_until_complete(asyncio.sleep(delay))


if __name__ == '__main__':
    shards_per_instance = 1
    total_shards = 10

    sharded = '--sharded' in sys.argv

    if sharded:
        print('Sharding enabled. Validating shard count...')
        if total_shards >= 40 and total_shards % 16 != 0:  # 40 * 2,500 = 100,000 (see: https://github.com/discordapp/discord-api-docs/issues/387)
            print('Bad shard count: total_shards must be a multiple of 16')
            sys.exit(0)

        total_instances = math.ceil(total_shards / shards_per_instance)
        print('Using {} instances'.format(total_instances))

        wait(5)

        for i in range(0, total_instances):
            start = i * shards_per_instance
            last = min(start + shards_per_instance, total_shards)
            ids = list(range(start, last))

            print('Appending instance {} to launch queue...'.format(i))
            instance_queue.append(PendingInstance(i, total_shards, ids))
    else:
        instance_queue.append(PendingInstance(0, 1, [0], launch_next_shard))

    launch_next_shard()

    try:
        while True:  # Keep the main process up
            wait(5)
    except KeyboardInterrupt:
        pass
