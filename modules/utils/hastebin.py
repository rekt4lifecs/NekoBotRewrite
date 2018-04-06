import aiohttp

async def post(content):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://hastebin.com/documents",
                                data=content.encode('utf-8')) as response:
            res = await response.json()
            return f"https://hastebin.com/{res['key']}"