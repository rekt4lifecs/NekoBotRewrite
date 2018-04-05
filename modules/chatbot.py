import discord, random, aiohttp

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

            async with aiohttp.ClientSession() as cs:
                terms = str(message.content[8:]).replace(" ", "%20")
                async with cs.get(f'http://www.cleverbot.com/getreply?key=CC82oN8K-J3GPoew961qiWJ5gWw&input={terms}') as r:
                    res = await r.json()
                    await channel.send(embed=discord.Embed(color=0xDEADBF, description=res['clever_output']))

            # # Questions
            # if content.endswith('?'):
            #     if str(content).isupper():
            #         await channel.send("Why u have to scream at me, i don't know 😭😭😭")
            #     else:
            #         lmgtfy = str(content[8:-1]).replace(" ", "+")
            #         lmgtfy = f"http://lmgtfy.com/?q={lmgtfy}"
            #         questions = ['hmmm', "I don't know.", f"Huh, let me google that for you <:DvaDab:404989452176588800>\n{lmgtfy}",
            #                      "I don't know daddy ;-;", "I didn't know that.", "wow, really?", "What does that mean?",
            #                      "Hmmm, let me think...", "Not sure....", "I think?", "Not so sure about that.", "ummmmm",
            #                      "Noppp", "uhhhhh", "hm?", "What?", "sorry was busy playing overwatch lol", "Yes", "No", "I dont know", "meh..."]
            #         await channel.send(random.choice(questions))

def setup(bot):
    n = Chatbot(bot)
    bot.add_listener(n.message_handler, "on_message")
    bot.add_cog(n)