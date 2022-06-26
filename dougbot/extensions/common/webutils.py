import aiohttp


async def is_file_url(url):
    return await is_link(url) and len(url[url.rfind('.'):]) in range(1, 6)


async def is_link(url):
    return url.startswith('https://') or url.startswith('www.') or url.startswith('http://')


async def url_get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as data:
            return await data.read()
