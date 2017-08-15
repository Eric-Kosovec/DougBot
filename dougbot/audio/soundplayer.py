from dougbot.util.queue import *


class SoundPlayer:
    def __init__(self):
        self.tracklist = Queue()
        self.playing = None
