from discord.ext import commands
import logging, traceback, sys, discord, json, dbl, asyncio, aiomysql
from datetime import date
from collections import Counter

import config

log = logging.getLogger('NekoBot')
log.setLevel(logging.DEBUG)
date = f"{date.today().timetuple()[0]}_{date.today().timetuple()[1]}_{date.today().timetuple()[2]}"
handler = logging.FileHandler(filename=f'NekoBot_{date}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

startup_extensions = {
    'modules.discordbots',
    'modules.fun',
    'modules.games',
    'modules.general',
    'modules.imgwelcome',
    'modules.mod',
    'modules.nsfw',
    'modules.reactions',
    'modules.eco',
    'modules.marriage'
}

class NekoBot(commands.AutoShardedBot):
    """NekoBot Rewrite OwO"""

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("n!"),
                         description=config.description,
                         pm_help=None,
                         help_attrs=dict(hidden=True))
        self.bot = NekoBot
        self.counter = Counter()

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
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
        if isinstance(exception, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
        elif isinstance(exception, commands.DisabledCommand):
            await ctx.send('This command is disabled...')
        elif isinstance(exception, commands.CommandInvokeError):
            em = discord.Embed(color=0xDEADBF,
                               title="Error",
                               description=f"Error in command {ctx.command.qualified_name}, [Support Server](https://discord.gg/q98qeYN)")
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
            await ctx.send("Im missing permissions ;-;")
        else:
            log.exception(type(exception).__name__, exc_info=exception)

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        # connection = await aiomysql.connect(user='root',
        #                                     password='rektdiscord',
        #                                     host='localhost',
        #                                     port=3306,
        #                                     db='nekobot')
        # async with connection.cursor() as cur:
        #     await cur.execute(f"SELECT amount FROM stats WHERE type = \"messages\"")
        #     messages = await cur.fetchone()
        #     messages = int(messages[0])
        #     await cur.execute(f"UPDATE stats SET amount = {messages + 1} WHERE type = \"messages\"")
        #     await connection.commit()
        #     if not await cur.execute(f'SELECT 1 FROM stalk WHERE userid = {message.author.id}'):
        #         await cur.execute(f"INSERT INTO stalk VALUES ({message.author.id}, 0)")
        #         await connection.commit()
        #     else:
        #         await cur.execute(f"SELECT messages FROM stalk WHERE userid = {message.author.id}")
        #         usermsg = await cur.fetchone()
        #         usermsg = int(usermsg[0])
        #         await cur.execute(f"UPDATE stalk SET messages = {usermsg + 1} WHERE userid = {message.author.id}")
        #         await connection.commit()

        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command(self, command):
        self.counter["commands"] += 1
        self.counter[commands] += 1
        # connection = await aiomysql.connect(user='root',
        #                                     password='rektdiscord',
        #                                     host='localhost',
        #                                     port=3306,
        #                                     db='nekobot')
        # async with connection.cursor() as cur:
        #     await cur.execute(f"SELECT amount FROM stats WHERE type = \"commands\"")
        #     commands = await cur.fetchone()
        #     commands = int(commands[0])
        #     await cur.execute(f"UPDATE stats SET amount = {commands + 1} WHERE type = \"commands\"")
        #     await connection.commit()

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_connect(self):
        print("Shard Connected...")

    async def on_ready(self):
        print("Ready OwO")
        print(self.shard_count)
        print(f"Servers {len(self.guilds)}")
        print(f"Users {len(set(self.get_all_members()))}")

    def run(self):
        super().run(config.token, reconnect=True)

def run_bot():
    bot = NekoBot()
    bot.run()

if __name__ == '__main__':
    run_bot()
