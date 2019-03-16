from .context import Context

class Command:

    def __init__(self, cmd):
        self.name = cmd.__name__
        self.help = cmd.__doc__
        self.cmd = cmd

    def invoke(self, ctx: Context, args):
        return self.cmd(ctx, args)

    def __repr__(self):
        return "<Command, name={}>".format(self.name)