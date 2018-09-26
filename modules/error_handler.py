from discord.ext import commands
import discord
import config, aiohttp, logging
import gettext

log = logging.getLogger()

class error_handler:

    def __init__(self, bot):
        self.bot = bot
        self.webhook_url = f"https://discordapp.com/api/webhooks/{config.webhook_id}/{config.webhook_token}"
        self.lang = {}
        for x in ["french", "polish", "spanish", "tsundere", "weeb"]:
            self.lang[x] = gettext.translation("errors", localedir="locale", languages=[x])

    async def _get_text(self, ctx):
        lang = await self.bot.get_language(ctx)
        if lang:
            return self.lang[lang].gettext
        else:
            return gettext.gettext

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    async def on_command_error(self, ctx, exception):

        error = getattr(exception, "original", exception)
        if isinstance(error, discord.NotFound):
            return
        elif isinstance(error, discord.Forbidden):
            return
        elif isinstance(error, discord.HTTPException) or isinstance(error, aiohttp.ClientConnectionError):
            async with aiohttp.ClientSession() as cs:
                webhook = discord.Webhook.from_url(self.webhook_url, adapter=discord.AsyncWebhookAdapter(cs))
                em = discord.Embed(color=16740159)
                em.title = "Error in command %s, Instance %s" % (ctx.command.qualified_name, self.bot.instance)
                em.description = "HTTPException"
                await webhook.send(embed=em)
            _ = await self._get_text(ctx)
            return await ctx.send(_("Failed to get data."))

        if isinstance(exception, commands.NoPrivateMessage):
            return
        elif isinstance(exception, commands.DisabledCommand):
            return
        elif isinstance(exception, commands.CommandInvokeError):
            payload = {
                "embeds": [
                    {
                        "title": f"Command: {ctx.command.qualified_name}, Instance: {self.bot.instance}",
                        "description": f"```py\n{exception}\n```\n By `{ctx.author}` (`{ctx.author.id}`)",
                        "color": 16740159
                    }
                ]
            }
            async with aiohttp.ClientSession() as cs:
                await cs.post(self.webhook_url, json=payload)
            em = discord.Embed(color=0xDEADBF,
                               title="Error",
                               description=f"Error in command {ctx.command.qualified_name}, "
                                           f"[Support Server](https://discord.gg/q98qeYN).\n`{exception}`")
            await ctx.send(embed=em)
            log.warning('In {}:'.format(ctx.command.qualified_name))
            log.warning('{}: {}'.format(exception.original.__class__.__name__, exception.original))
        elif isinstance(exception, commands.BadArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.MissingRequiredArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.CheckFailure):
            _ = await self._get_text(ctx)
            await ctx.send(_('You are not allowed to use that command.'), delete_after=5)
        elif isinstance(exception, commands.CommandOnCooldown):
            _ = await self._get_text(ctx)
            await ctx.send(_('Command is on cooldown... {:.2f}s left').format(exception.retry_after), delete_after=5)
        elif isinstance(exception, commands.CommandNotFound):
            return
        else:
            return

def setup(bot):
    bot.add_cog(error_handler(bot))