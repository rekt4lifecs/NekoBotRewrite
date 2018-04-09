import time
starttime = time.time()
from discord.ext import commands
import logging, traceback, sys, discord
from datetime import date
from collections import Counter
import aiomysql

import config
log = logging.getLogger('NekoBot')
log.setLevel(logging.INFO)
date = f"{date.today().timetuple()[0]}_{date.today().timetuple()[1]}_{date.today().timetuple()[2]}"
handler = logging.FileHandler(filename=f'NekoBot_{date}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

startup_extensions = {
    'modules.audio',
    'modules.cardgame',
    'modules.chatbot',
    'modules.discordbots',
    'modules.donator',
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

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('n!'),
                         description="NekoBot",
                         shard_count=10,
                         pm_help=None,
                         help_attrs={'hidden': True})
        self.counter = Counter()
        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except:
                print("Failed to load {}.".format(extension), file=sys.stderr)
                traceback.print_exc()

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
        channel = self.get_channel(431987399581499403)
        if isinstance(exception, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
        elif isinstance(exception, commands.DisabledCommand):
            await ctx.send('This command is disabled...')
        elif isinstance(exception, commands.CommandInvokeError):
            em = discord.Embed(color=0xDEADBF,
                               title="Error",
                               description=f"Error in command {ctx.command.qualified_name}, "
                                           f"[Support Server](https://discord.gg/q98qeYN)")
            await channel.send(embed=discord.Embed(color=0xff6f3f,
                                                   title="Command Error").add_field(name=f"Command: {ctx.command.qualified_name}",
                                                                                    value=f"```py\n{exception}```"))
            try:
                owner = self.owner_id
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
        elif isinstance(exception, discord.Forbidden):
            pass
        elif isinstance(exception, discord.LoginFailure):
            print("Failed to login. Invalid token?")
        elif isinstance(exception, discord.DiscordException):
            print(f"Discord Exception, {exception}")
        elif isinstance(exception, discord.NotFound):
            pass
        else:
            log.exception(type(exception).__name__, exc_info=exception)
            await channel.send(embed=discord.Embed(color=0xff6f3f, title="Unknown Error", description=f"{exception}"))

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.close()

    async def on_shard_ready(self, shard_id):
        print(f"Shard {shard_id} Connected...")

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

    def run(self):
        super().run(config.token)

def run_bot():
    bot = NekoBot()
    bot.run()

if __name__ == '__main__':
    run_bot()
