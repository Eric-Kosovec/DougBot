
class Track:

    def __init__(self, src, is_link, repeat=1):
        self.src = src
        self.is_link = is_link
        self.repeat = repeat

        if not self.is_link:
            # Will throw IOError if file doesn't exist.
            with open(self.src, 'r'):
                pass
