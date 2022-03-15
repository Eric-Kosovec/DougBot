from threading import Semaphore


class Track:

    def __init__(self, ctx, source, repeat=1, callback=None):
        self.ctx = ctx
        self.source = source
        self.repeat = repeat
        self.callback = callback
        self.uploader = ''
        self.title = ''
        self.thumbnail = ''
        self.duration = 0
        self._ready_lock = Semaphore(0)

    def wait_for_ready(self):
        self._ready_lock.acquire()

    def signal_ready(self):
        self._ready_lock.release()
