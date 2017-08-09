from src.util.Queue import *


class SoundPlayer:
    def __init__(self):
        self.tracklist = Queue()
        self.playing = None
