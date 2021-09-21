import urllib.parse


def sanitize_url(url: str):
    if url is None:
        return None
    return urllib.parse.unquote_plus(url).replace('..', '')
