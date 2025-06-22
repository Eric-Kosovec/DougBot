from threading import Semaphore


class Track:

    def __init__(self, ctx, voice, src, is_link, repeat=1):
        self.ctx = ctx
        self.voice = voice
        self.src = src
        self.is_link = is_link
        self.repeat = repeat
        self._ready_notification = Semaphore(0)

    def mark_ready(self):
        self._ready_notification.release()

    def wait_for_ready(self):
        self._ready_notification.acquire()
