from urllib.parse import urlparse

import aiohttp

HTTP = 'http://'
HTTPS = 'https://'
WWW = 'www.'


async def is_link(url):
    test_url = url.strip()

    if not test_url.startswith((HTTP, HTTPS)):
        test_url = f'{HTTPS}{test_url}'

    try:
        parsed = urlparse(test_url)

        if not parsed.netloc or '.' not in parsed.netloc:
            return False

        response = await url_head(test_url)
        return response.status == 200 and len(response.headers) > 0
    except Exception:
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
