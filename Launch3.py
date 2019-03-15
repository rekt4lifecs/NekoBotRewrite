
import shardedBot2

class Pipe:
    closed = True

if __name__ == "__main__":
    shardedBot2.NekoBot(3, 8, 128, [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63], Pipe(), None)
