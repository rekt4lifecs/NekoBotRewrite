from discord.ext import commands

# https://github.com/KawaiiBot/IPC-Server
#
# MIT License
#
# Copyright (c) 2018 KawaiiDevs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class IPC:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def instance(self, ctx):
        """ Displays the current instance ID """
        await ctx.send(self.bot.instance)

    @commands.command(name="global")
    @commands.is_owner()
    async def global_(self, ctx, command: str, *, args: str):
        """ Executes the specified command across the other instances
        Command  |  Arguments  |  Returns
        eval        *             *
        reload      cog           bool
        """
        data = {
            'op': 'EXEC',
            'id': self.bot.instance,
            'd': {
                'command': command,
                'args': args
            }
        }
        res = await self.bot.conn.send(data, expect_result=True)
        await ctx.send(f"```py\n{str(res)}\n```")


def setup(bot):
    bot.add_cog(IPC(bot))