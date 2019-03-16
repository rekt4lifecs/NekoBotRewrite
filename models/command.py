from .context import Context
from inspect import getfullargspec

class Command:

    def __init__(self, cmd, *, hidden: bool = False, name: str = None):
        self.name = cmd.__name__ if name is None else name
        self.help = cmd.__doc__
        self.hidden = hidden
        self.cmd = cmd
        self.required_arguments = getfullargspec(cmd).args

    async def invoke(self, ctx: Context, args):
        args.pop(0)
        await self.cmd(ctx, *args)

    def __repr__(self):
        return "<Command, name={}>".format(self.name)