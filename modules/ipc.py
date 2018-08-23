import rethinkdb as r
import asyncio, aiohttp
import discord
from discord.ext import commands
from hooks import ipc as ipchook

class IPC:

    def __init__(self, bot):
        self.bot = bot
        self.has_started = False
        self.webhook = ipchook

    async def __post_hook(self, action:str):
        async with aiohttp.ClientSession() as cs:
            webhook = discord.Webhook.from_url(self.webhook, adapter=discord.AsyncWebhookAdapter(cs))
            await webhook.send("Action: %s\nInstance: %s" % (action, self.bot.instance))

    async def __ipc_loop(self):
        if not self.has_started:
            self.has_started = True
        while self.has_started:
            try:
                [(await self.bot.redis.set(f"shard:{x[0]}", str(round(x[1] * 1000, 2)))) for x in self.bot.latencies]
            except:
                print("Failed to update latencies")
            data = await r.table("ipc").get("ipc").run(self.bot.r_conn)
            if not data[str(self.bot.instance)] == "":
                if data[str(self.bot.instance)] == "ping":
                    await self.__post_hook("Ping - %s" % self.bot.instance)
                if data[str(self.bot.instance)] == "shutdown":
                    await self.__post_hook("Shutting down... bai")
                    await self.bot.close()
                else:
                    await self.__post_hook("Reloaded " + data[str(self.bot.instance)])
                    try:
                        self.bot.unload_extension("modules.%s" % data[str(self.bot.instance)])
                        self.bot.load_extension("modules.%s" % data[str(self.bot.instance)])
                    except:
                        print("Failed to reload")
                        pass
                await r.table("ipc").get("ipc").update({str(self.bot.instance): ""}).run(self.bot.r_conn)
            await asyncio.sleep(30)

    @commands.group(hidden=True)
    @commands.is_owner()
    async def ipc(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("```\nHeccin ipc finally /shrug\n\nreload - reload shit\nforce - force loop\nshutdown - bai```")

    @ipc.command(name="shutdown")
    async def ipc_shutdown(self, ctx):
        """bai"""
        await r.table("ipc").get("ipc").update({"0": "shutdown",
                                                "1": "shutdown",
                                                "2": "shutdown",
                                                "3": "shutdown"}).run(self.bot.r_conn)

    @ipc.command(name="reload")
    async def ipc_reload(self, ctx, module:str):
        """reload shit"""
        await r.table("ipc").get("ipc").update({"0": module, "1": module, "2": module, "3": module}).run(self.bot.r_conn)
        await ctx.send("Added to queue")

    @ipc.command(name="ping")
    async def ipc_ping(self, ctx):
        """Ping ipc"""
        await ctx.send("Sending ping")
        await r.table("ipc").get("ipc").update({"0": "ping", "1": "ping", "2": "ping", "3": "ping"}).run(self.bot.r_conn)

    @ipc.command(name="force")
    async def ipc_force(self, ctx):
        await ctx.send("Forcing loop")
        await self.__ipc_loop()

    async def on_ready(self):
        await self.__ipc_loop()

def setup(bot):
    bot.add_cog(IPC(bot))