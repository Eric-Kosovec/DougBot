from threading import Semaphore


class Playlist:

    def __init__(self, path, tracks=None):
        self.path = path
        self.tracks = [] if tracks is None else tracks
        self.current_track = 0
        self._valid = True
        self._ready_lock = Semaphore(0)

    def invalidate(self):
        self._valid = False

    def add_track(self, track):
        self.tracks.append(track)

    def remove_track(self, track):
        try:
            self.tracks.remove(track)
        except ValueError:
            pass
