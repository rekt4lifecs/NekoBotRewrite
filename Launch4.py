
import shardedBot2

class Pipe:
    closed = True

if __name__ == "__main__":
    shardedBot2.NekoBot(4, 8, 128, [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79], Pipe(), None)
