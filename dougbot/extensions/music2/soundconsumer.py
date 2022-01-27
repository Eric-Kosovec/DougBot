import inspect
import logging
from queue import Queue
from threading import Lock, Semaphore

import discord


class SoundConsumer:

    __sound_consumer = None

    @classmethod
    def instance(cls, bot, callback=None, notify_lock=None):
        if cls.__sound_consumer is None:
            cls.__sound_consumer = SoundConsumer(bot, callback, notify_lock)
        return cls.__sound_consumer

    def __init__(self, bot, callback, notify_lock):
        self.bot = bot
        self.loop = self.bot.loop
        self._callback = callback
        self._notify_lock = notify_lock

        self._run = False
        self._skip = False

        self._queue = Queue()  # Thread-safe queue
        self._done_playing_lock = Semaphore(0)

    def run(self):
        self._run = True
        while self._run:
            track = self._queue.get()
            track.wait_for_ready()

    def skip(self):
        self._skip = True

    def stop(self):
        # TODO BREAK OUT OF LOOP OR EXIT THREAD
        self._run = False

    def is_running(self):
        return self._run

    def enqueue(self, track):
        if track is not None:
            self._queue.put_nowait(track)
