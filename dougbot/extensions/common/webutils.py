import requests


async def is_file_url(url):
    return await is_link(url) and len(url[url.rfind('.'):]) in range(1, 6)


async def async_is_link(url):
    return url.startswith('https://') or url.startswith('http://') or url.startswith('www.')


def is_link(url):
    return url.startswith('https://') or url.startswith('http://') or url.startswith('www.')


async def download_file(url):
    if not await is_file_url(url):
        return b''
    return requests.get(url, stream=True)
