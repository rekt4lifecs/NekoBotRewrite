
import shardedBot2

class Pipe:
    closed = True

if __name__ == "__main__":
    shardedBot2.NekoBot(0, 8, 128, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], Pipe(), None)
