class Context:

    def __init__(self, bot, message, command):
        self.message = message
        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild
        self.bot = bot
        self.command = command

    async def send(self, *args, **kwargs):
        return await self.channel.send(*args, **kwargs)

    def __repr__(self):
        return "<Context - Content: {} - Author: {}>".format(self.message.content, self.author.id)
