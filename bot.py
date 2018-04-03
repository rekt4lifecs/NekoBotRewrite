from discord.ext import commands
import logging, traceback, sys, discord
from datetime import date
from collections import Counter
import raven

import config

sentry = raven.Client(config.sentry)

log = logging.getLogger('NekoBot')
log.setLevel(logging.DEBUG)
date = f"{date.today().timetuple()[0]}_{date.today().timetuple()[1]}_{date.today().timetuple()[2]}"
handler = logging.FileHandler(filename=f'NekoBot_{date}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

# 'modules.devtools',
# 'modules.mod',
# 'modules.discordbots',
# 'modules.fun',
# 'modules.games',
# 'modules.general',
# 'modules.imgwelcome',
# 'modules.nsfw',
# 'modules.reactions',
# 'modules.eco',
# 'modules.marriage',
# 'modules.crypto'

startup_extensions = {
    'modules.cardgame',
    'modules.chatbot',
    'modules.crypto',
    'modules.discordbots',
    'modules.eco',
    'modules.fun',
    'modules.games',
    'modules.general',
    'modules.imgwelcome',
    'modules.marriage',
    'modules.mod',
    'modules.nsfw',
    'modules.reactions'
}

class NekoBot(commands.AutoShardedBot):
    """NekoBot Rewrite OwO"""

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('n!'),
                         description=config.description,
                         pm_help=None,
                         help_attrs=dict(hidden=True))
        self.bot = NekoBot
        self.counter = Counter()

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
        elif isinstance(exception, commands.DisabledCommand):
            await ctx.send('This command is disabled...')
        elif isinstance(exception, commands.CommandInvokeError):
            em = discord.Embed(color=0xDEADBF,
                               title="Error",
                               description=f"Error in command {ctx.command.qualified_name}, [Support Server](https://discord.gg/q98qeYN)")
            sentry.captureMessage(f'Error in command {ctx.command.qualified_name}, {exception.original}')
            try:
                owner = self.bot.get_user(270133511325876224)
                await owner.send(f"Error in `{ctx.command.qualified_name}`\n```\n{exception}\n```")
            except:
                pass
            await ctx.send(embed=em)
            print('In {}:'.format(ctx.command.qualified_name), file=sys.stderr)
            traceback.print_tb(exception.original.__traceback__)
            print('{}: {}'.format(exception.original.__class__.__name__, exception.original), file=sys.stderr)
        elif isinstance(exception, commands.BadArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.MissingRequiredArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.CheckFailure):
            await ctx.send('You are not allowed to use that command.')
        elif isinstance(exception, commands.CommandOnCooldown):
            await ctx.send('Command is on cooldown... {:.2f}s left'.format(exception.retry_after))
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.BotMissingPermissions):
            await ctx.send(f"Im missing permissions ;-;\nPermissions I need:\n{exception.missing_perms}")
        else:
            log.exception(type(exception).__name__, exc_info=exception)
            sentry.captureMessage(exception)

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command(self, command):
        self.counter["commands"] += 1

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_connect(self):
        print("Shard Connected...")

    async def on_ready(self):
        print("             _         _           _   \n"
              "            | |       | |         | |  \n"
              "  _ __   ___| | _____ | |__   ___ | |_ \n"
              " | '_ \ / _ \ |/ / _ \| '_ \ / _ \| __|\n"
              " | | | |  __/   < (_) | |_) | (_) | |_ \n"
              " |_| |_|\___|_|\_\___/|_.__/ \___/ \__|\n"
              "                                       \n"
              "                                       ")
        print("Ready OwO")
        print(f"Shards: {self.shard_count}")
        print(f"Servers {len(self.guilds)}")
        print(f"Users {len(set(self.get_all_members()))}")
        await self.change_presence(status=discord.Status.idle)
        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print("Failed to load {}.".format(extension), file=sys.stderr)
                traceback.print_exc()
                sentry.captureException()

    def run(self):
        super().run(config.token)

def run_bot():
    bot = NekoBot()
    bot.run()

if __name__ == '__main__':
    run_bot()
