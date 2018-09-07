
from dougbot.core.command import CommandError


class Track:

    def __init__(self, src, is_link):
        self.src = src
        self.is_link = is_link

        if not self.is_link:
            try:
                with open(self.src, 'r'):
                    pass
            except IOError:
                raise CommandError(f'Track {self.src} does not exist')
