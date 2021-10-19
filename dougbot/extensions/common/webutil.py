import requests


async def is_file_url(url):
    return url is not None and await is_link(url) and '.' in url


async def is_link(url):
    return url.startswith('https://') or url.startswith('http://') or url.startswith('www.')


async def download_file(url):
    if not await is_file_url(url):
        return b''
    return requests.get(url, stream=True)
