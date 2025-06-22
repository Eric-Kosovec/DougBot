import inspect
from queue import Empty
from queue import Queue
from threading import Lock, Semaphore

import nextcord

from dougbot.common.logger import Logger

_FFMPEG_OPTIONS = '-loglevel quiet'


class SoundConsumer:
    __sound_consumer_lock = Lock()
    __sound_consumer = None

    @classmethod
    def get_sound_consumer(cls, bot, callback=None, notify_lock=None):
        with cls.__sound_consumer_lock:
            if cls.__sound_consumer is None:
                cls.__sound_consumer = SoundConsumer(bot, callback, notify_lock)
            return cls.__sound_consumer

    def __init__(self, bot, callback=None, notify_lock=None):
        self.bot = bot
        self.loop = bot.loop
        self._callback = callback
        self._notify_lock = notify_lock

        self._stop = False
        self._skip = False
        self._voice = None
        self._queue = Queue()  # Thread-safe queue
        self._done_playing_lock = Semaphore(0)

    def enqueue(self, track):
        if track is not None:
            self._queue.put_nowait(track)

    def run(self):
        while True:
            track = self._queue.get()

            if self._stop:
                self._clear_queue()
                continue

            for _ in range(track.repeat):
                if self._stop or self._skip:
                    break

                self._voice = track.voice

                source = self._make_audio_source(track)

                if not source:
                    continue

                try:
                    self._voice.play(source, after=self._finished)
                    self._done_playing_lock.acquire()
                except Exception as e:
                    Logger(__file__) \
                        .message('SoundConsumer failed to play') \
                        .exception(e) \
                        .error()

            self._queue.task_done()
            self._skip = False

            if self._callback is not None:
                if inspect.iscoroutinefunction(self._callback):
                    self.loop.call_soon_threadsafe(self._callback, track)
                else:
                    self._callback(track)

            if self._notify_lock is not None:
                self._notify_lock.release()

    # TODO LOCK AROUND SKIP/STOP???
    def skip_track(self):
        if self._queue.empty() and not self._voice.is_playing():
            return
        self._skip = True
        if self._voice is not None and self._voice.is_playing():
            self._voice.stop()

    def stop_playing(self):
        self._stop = True
        if self._voice is not None and self._voice.is_playing():
            self._voice.stop()
        self._queue.join()
        self._stop = False

    def _clear_queue(self):
        try:
            while True:
                self._queue.get_nowait()
                self._queue.task_done()
        except Empty | ValueError:
            pass

    def _finished(self, error):
        if error is not None:
            Logger(__file__) \
                .message('SoundConsumer playing error') \
                .exception(error) \
                .error()

        self._done_playing_lock.release()

    @staticmethod
    def _make_audio_source(track):
        try:
            source = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio(track.src, options=_FFMPEG_OPTIONS))
            source.volume = 1.0
            return source
        except Exception as e:
            Logger(__file__) \
                .message('Failed to make audio source') \
                .exception(e) \
                .error()

            return None
