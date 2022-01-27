from threading import Semaphore


class Track:

    def __init__(self, ctx, voice, source, repeat=1):
        self.ctx = ctx
        self.voice = voice
        self.source = source
        self.repeat = repeat
        self.uploader = ''
        self.title = ''
        self.thumbnail = ''
        self.duration = 0
        self._valid = True
        self._ready_lock = Semaphore(0)

    def invalidate(self):
        self._valid = False

    def wait_for_ready(self):
        self._ready_lock.acquire()

    def signal_ready(self):
        self._ready_lock.release()
