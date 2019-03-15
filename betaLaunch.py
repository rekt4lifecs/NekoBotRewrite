from config import testtoken
import shardedBot2

class Pipe:
    def __init__(self):
        self.closed = True

if __name__ == "__main__":
    client = shardedBot2.NekoBot(0, 0, 1, [0], Pipe(), None)
    client.run(testtoken)
