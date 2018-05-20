import aiohttp

async def post(content):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://haste.nekobot.xyz/documents",
                                data=content.encode('utf-8')) as response:
            res = await response.json()
            return f"https://haste.nekobot.xyz/{res['key']}"