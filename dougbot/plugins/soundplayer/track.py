
from dougbot.core.command import CommandError


class Track:

    def __init__(self, src, is_link):
        self._src = src
        self._is_link = is_link

        if not self._is_link:
            try:
                with open(self._src, 'r'):
                    pass
            except IOError:
                raise CommandError(f'Track {self._src} does not exist')

    def get_source(self):
        return self._src

    def is_link(self):
        return self._is_link
