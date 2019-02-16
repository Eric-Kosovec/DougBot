import aiohttp


async def download_file(url):
    with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            return await response.read()


async def download_multiple(urls):
    # TODO
    return None
