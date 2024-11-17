import re


def remove_playlist(url):
    return re.sub(r'&list=[a-zA-Z0-9_-]+', '', url)
