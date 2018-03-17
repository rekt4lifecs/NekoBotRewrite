from discord.ext import commands
import asyncio

class DevTools:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def latency(self, ctx):
        latency1 = "%.4f" % self.bot.latencies[0][1]
        latency2 = "%.4f" % self.bot.latencies[1][1]
        latency3 = "%.4f" % self.bot.latencies[2][1]
        msg = await ctx.send(f"Shard1: {latency1}\nShard2: {latency2}\nShard3: {latency3}")
        msg
        for x in range(5):
            await asyncio.sleep(10)
            latency1 = "%.4f" % self.bot.latencies[0][1]
            latency2 = "%.4f" % self.bot.latencies[1][1]
            latency3 = "%.4f" % self.bot.latencies[2][1]
            await msg.edit(content=f"Shard1: {latency1}\nShard2: {latency2}\nShard3: {latency3}")

def setup(bot):
    bot.add_cog(DevTools(bot))