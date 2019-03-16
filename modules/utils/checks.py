from functools import wraps

def has_permissions(**perms):
    def wrapper(func):
        @wraps(func)
        async def wrapped(ctx, args):
            if ctx.author.id == 270133511325876224:
                return await func(ctx, args)
            resolved = ctx.channel.permissions_for(ctx.author)
            if all(getattr(resolved, name, None) == value for name, value in perms.items()):
                return await func(ctx, args)
        return wrapped
    return wrapper

def is_owner():
    def wrapper(func):
        @wraps(func)
        async def wrapped(ctx, args):
            if ctx.author.id == 270133511325876224:
                return await func(ctx, args)
        return wrapped
    return wrapper
