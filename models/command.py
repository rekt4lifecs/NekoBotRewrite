from .context import Context

class Command:

    def __init__(self, cmd, *, hidden: bool = False, name: str = None, aliases: list = list()):
        self.name = cmd.__name__ if name is None else name
        self.help = cmd.__doc__
        self.aliases = aliases
        self.hidden = hidden
        self.cmd = cmd

    async def invoke(self, ctx: Context, args):
        args.pop(0)
        await self.cmd(ctx, *args)

    def __repr__(self):
        return "<Command, name={}>".format(self.name)
