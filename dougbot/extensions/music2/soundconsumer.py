import asyncio
import logging
from queue import Empty
from queue import Queue
from threading import Semaphore

from nextcord import FFmpegPCMAudio
from nextcord import PCMVolumeTransformer


class SoundConsumer:

    __sound_consumer = None

    @classmethod
    def instance(cls, bot, notify_callback=None):
        if cls.__sound_consumer is None:
            cls.__sound_consumer = SoundConsumer(bot, notify_callback)
        return cls.__sound_consumer

    def __init__(self, bot, notify_callback):
        self.bot = bot
        self.loop = self.bot.loop
        self._notify_callback = notify_callback
        self._volume = 0

        self._track = None
        self._stop = False
        self._skip = False
        self._run = False
        self._audio_source = None

        self._queue = None
        self._done_playing_lock = None

    def run(self, volume):
        self._volume = volume
        self._done_playing_lock = Semaphore(0)
        self._queue = Queue()

        self._stop = False
        self._skip = False
        self._run = True
        while self._run:
            self._track = self._queue.get()
            self._track.wait_for_ready()

            if self._notify_callback is not None:
                asyncio.run_coroutine_threadsafe(self._notify_callback(self._track), self.loop)

            for _ in range(self._track.repeat):
                if self._stop or self._skip or not self._run:
                    break
                self._audio_source = self._create_audio_source(self._track, self._volume)
                self._track.voice.play(self._audio_source, after=self._finished)
                self._done_playing_lock.acquire()

            self._skip = False
            self._queue.task_done()

            if self._stop:
                self._clear_queue()
                self._stop = False

    def kill(self):
        self._stop = True
        self._run = False
        self._stop_current()
        self._skip = False

    def skip(self):
        self._skip = True
        self._stop_current()

    def stop(self):
        self._stop = True
        self._stop_current()

    def is_running(self):
        return self._run

    def enqueue(self, track):
        if track is not None:
            self._queue.put_nowait(track)

    def _finished(self, error):
        if error is not None:
            logging.getLogger(__file__).log(logging.ERROR, f'SoundPlayer finished error: {error}')
        self._volume = self._audio_source.volume
        self._done_playing_lock.release()

    def _clear_queue(self):
        try:
            while True:
                self._queue.get_nowait()
                self._queue.task_done()
        except Empty as _:
            pass

    def _stop_current(self):
        try:
            if self._track is not None and self._track.voice is not None:
                self._track.voice.stop()
                self._track.voice = None
        except AttributeError as _:
            pass

    @staticmethod
    def _create_audio_source(track, volume):
        return PCMVolumeTransformer(FFmpegPCMAudio(track.src, options='-loglevel quiet'), volume)
