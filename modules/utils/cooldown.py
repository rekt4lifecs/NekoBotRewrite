from functools import wraps
from time import time

def Cooldown(cooldown_time: int):
    def wrapper(func):
        @wraps(func)
        async def wrapped(ctx, args):
            data = await ctx.bot.redis.get("cooldown:{}:{}".format(ctx.command.name, ctx.author.id))
            if data is not None:
                raise ValueError("Command is on cooldown... {}s left".format(int(data) - int(time())))
            await ctx.bot.redis.set("cooldown:{}:{}".format(ctx.command.name, ctx.author.id), int(time() + cooldown_time), expire=cooldown_time)
            return await func(ctx, args)
        return wrapped
    return wrapper
