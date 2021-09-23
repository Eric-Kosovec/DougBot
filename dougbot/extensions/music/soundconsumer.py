import logging

import discord


class SoundConsumer:

    def __init__(self, bot, queue, done_playing_lock, volume, channel=None, voice=None):
        self._bot = bot
        self._queue = queue
        self._done_playing_lock = done_playing_lock
        self._volume = volume
        self._channel = channel
        self._voice = voice
        self._run = False
        self._skip = False

    def run(self):
        self._run = True
        while self._run:
            track = self._queue.get()

            if not self._run:
                break

            if self._voice is None and self._channel is not None:
                self._voice = self._bot.loop.run_until_complete(self._bot.join_voice_channel(self._channel))

            for _ in range(track.repeat):
                if self._skip:
                    self._skip = False
                    break
                self._voice.play(self._create_audio_source(track), after=self._finished)
                self._done_playing_lock.acquire()

    def set_voice(self, voice):
        self._voice = voice

    def set_channel(self, channel):
        self._channel = channel

    def _finished(self, error):
        if error is not None:
            logging.getLogger(__file__).log(logging.ERROR, f'SoundPlayer finished error: {error}')
        self._done_playing_lock.release()

    def _create_audio_source(self, track):
        audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track.src, options='-loglevel quiet'))
        audio_source.volume = self._volume
        return audio_source
