import discord, aiohttp

class Chatbot:

    def __init__(self, bot):
        self.bot = bot

    async def message_handler(self, message):
        channel = message.channel
        content = message.content

        if content.startswith('you gay nekobot') or content.startswith('You gay nekobot?') or content.startswith("YOU GAY NEKOBOT"):
            await channel.send("Yes daddy, 👉👈😩💦")
            return

        if content.startswith("nekobot ") or content.startswith("NekoBot ") or content.startswith("NEKOBOT ") or content.startswith("Nekobot "):
            await channel.trigger_typing()

            async with aiohttp.ClientSession(headers={"Authorization": "Bearer a7d6414f118443bc8653c9dc9f36dc06"}) as cs:
                terms = str(message.content[8:]).replace(" ", "%20")
                async with cs.get(f'https://api.dialogflow.com/v1/query?v=20150910&lang=en&query={terms}&sessionId=0') as r:
                    res = await r.json()
                    await channel.send(embed=discord.Embed(color=0xDEADBF, description=res['result']['fulfillment']['messages'][0]['speech']))

def setup(bot):
    n = Chatbot(bot)
    bot.add_listener(n.message_handler, "on_message")
    bot.add_cog(n)