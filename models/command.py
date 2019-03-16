from .context import Context

class Command:

    def __init__(self, cmd, *, hidden: bool = False, name: str = None):
        self.name = cmd.__name__ if name is None else name
        self.help = cmd.__doc__
        self.hidden = hidden
        self.cmd = cmd

    def invoke(self, ctx: Context, args):
        return self.cmd(ctx, args)

    def __repr__(self):
        return "<Command, name={}>".format(self.name)