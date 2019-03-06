from dougbot.extensions.soundplayer.error import TrackNotExistError


class Track:

    def __init__(self, src, is_link):
        self.src = src
        self.is_link = is_link

        if not self.is_link:
            try:
                with open(self.src, 'r'):
                    pass
            except IOError:
                raise TrackNotExistError()
