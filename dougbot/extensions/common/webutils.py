import aiohttp

HTTP = 'http://'
HTTPS = 'https://'
WWW = 'www.'


async def is_link(url):
    if url.startswith(HTTPS) or url.startswith(WWW) or url.startswith(HTTP):
        try:
            response = await url_head(url)
            return response.status == 200 and len(response.headers) > 0
        except Exception:
            pass

    return False


async def url_get(url):
    url = await _normalize_url(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as data:
            return await data.read()


async def url_head(url):
    url = await _normalize_url(url)
    async with aiohttp.request('HEAD', url) as response:
        return response


async def _normalize_url(url):
    if url.startswith(WWW):
        return HTTPS + url
    elif url.startswith(HTTP):
        return url.replace(HTTP, HTTPS, 1)
    return url
