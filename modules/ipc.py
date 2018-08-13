import rethinkdb as r
import asyncio, aiohttp
import discord
from discord.ext import commands

class IPC:

    def __init__(self, bot):
        self.bot = bot
        self.has_started = False
        self.webhook = ""

    async def __post_hook(self, action:str):
        async with aiohttp.ClientSession() as cs:
            webhook = discord.Webhook.from_url(self.webhook, adapter=discord.AsyncWebhookAdapter(cs))
            await webhook.send("Action: %s\nInstance: %s" % (action, self.bot.instance))

    async def __ipc_loop(self):
        if not self.has_started:
            self.has_started = True
        while self.has_started:
            data = await r.table("ipc").get("ipc").run(self.bot.r_conn)
            if not data[str(self.bot.instance)] == "":
                await self.__post_hook("Reloaded " + data[str(self.bot.instance)])
                try:
                    self.bot.unload_extension("modules.%s" % data[str(self.bot.instance)])
                    self.bot.load_extension("modules.%s" % data[str(self.bot.instance)])
                except:
                    print("Failed to reload")
                    pass
                await r.table("ipc").get("ipc").update({str(self.bot.instance): ""}).run(self.bot.r_conn)
            else:
                await self.__post_hook("Pong!")
            await asyncio.sleep(30)

    @commands.group(hidden=True)
    @commands.is_owner()
    async def ipc(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("```\nHeccin ipc finally /shrug\n\nreload - reload shit\nforce - force loop\n```")

    @ipc.command(name="reload")
    async def ipc_reload(self, ctx, module:str):
        """reload shit"""
        await r.table("ipc").get("ipc").update({"0": module, "1": module, "2": module}).run(self.bot.r_conn)
        await ctx.send("Added to queue")

    @ipc.command(name="force")
    async def ipc_force(self, ctx):
        await ctx.send("Forcing loop")
        await self.__ipc_loop()

    async def on_ready(self):
        await self.__ipc_loop()

def setup(bot):
    bot.add_cog(IPC(bot))