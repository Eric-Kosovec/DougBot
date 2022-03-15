import asyncio
from queue import Empty
from queue import Queue
from threading import Semaphore

from nextcord import FFmpegPCMAudio
from nextcord import PCMVolumeTransformer

from dougbot.common.logevent import LogEvent
from dougbot.core.bot import DougBot


class SoundConsumer:
    __sound_consumer = None

    # TODO HAVE THE PROBLEM OF WHEN SOUNDPLAYER REQUESTS A STOP, IT WILL STOP ALL TRACKS - EVEN ONES FOR DIFFERENT CHANNEL

    @classmethod
    def instance(cls, bot):
        if cls.__sound_consumer is None:
            cls.__sound_consumer = SoundConsumer(bot)
        return cls.__sound_consumer

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.loop = self.bot.loop

        self._volume = 0
        self._stop = False
        self._skip = False
        self._run = False
        self._channel = None
        self._voice = None
        self._audio_source = None

        self._queue = None
        self._done_playing_lock = None

    def run(self, volume):
        self._volume = volume
        self._queue = Queue()
        self._done_playing_lock = Semaphore(0)
        self._voice = None

        self._stop = False
        self._skip = False
        self._run = True

        while self._run:
            track = self._pull_track()

            if track.channel != self._channel:  # TODO TRACK DOESNT HAVE CHANNEL ON IT
                self._channel = track.ctx.message.author.voice.channel
                self._voice = self._join_voice_channel(self._channel)

            for _ in range(track.repeat):
                if self._stop or self._skip or not self._run:
                    break
                self._audio_source = self._create_audio_source(track, self._volume)
                self._voice.play(self._audio_source, after=self._finished)
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

    def _pull_track(self):
        track = self._queue.get()
        track.wait_for_ready()

        if track.callback:
            asyncio.run_coroutine_threadsafe(track.callback(track), self.loop)

        return track

    def _finished(self, error):
        if error:
            LogEvent(__file__) \
                .message('SoundPlayer finished error') \
                .exception(error) \
                .error()

        self._volume = self._audio_source.volume
        self._done_playing_lock.release()

    def _clear_queue(self):
        try:
            while True:
                self._queue.get_nowait()
                self._queue.task_done()
        except Empty | ValueError:
            pass

    def _stop_current(self):
        try:
            if self._voice is not None:
                self._voice.stop()
                self._voice = None
        except AttributeError:
            pass

    def _join_voice_channel(self, channel):
        return asyncio.run_coroutine_threadsafe(self.bot.join_voice_channel(channel), self.loop).result()

    @staticmethod
    def _create_audio_source(track, volume):
        return PCMVolumeTransformer(FFmpegPCMAudio(track.src, options='-loglevel quiet'), volume)
