import os
import threading
from asyncio.locks import Semaphore

from dougbot.plugins.plugin import Plugin
from dougbot.plugins.util.join import bot_join, bot_leave
from dougbot.plugins.soundplayer.track import Track
from dougbot.util.queue import Queue
from dougbot.util.cache import LRUCache


class SoundPlayer(Plugin):

    _CLIPS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _CLIPS_DIR = os.path.join(_CLIPS_DIR, 'res', 'sbsounds')

    def __init__(self):
        super().__init__()
        self.path_cache = LRUCache(10)
        self.sound_queue = Queue()
        self.play_lock = None
        self.first_play = True
        self.playing = False
        self.voice = None
        self.volume = 1.0

    @Plugin.command('join')
    async def join(self, event):
        if event is None or event.channel.is_private or self.voice is not None:
            return

        self.voice = await bot_join(event)
        print(self.voice)

        self.playing = False
        self.first_play = True
        self.play_lock = Semaphore(0, loop=event.event_loop)

    @Plugin.command('leave')
    async def leave(self, event):
        if event is None or event.channel.is_private:
            return

        # User is not in a voice channel
        if not event.author.voice.voice_channel:
            return

        self.play_lock.release()
        self.play_lock = None
        self.voice = None
        self.playing = False

        await bot_leave(event)

    @Plugin.command(['sb', 'play'], 'str')
    async def play(self, event, audio):
        if event is None or audio is None:
            return

        await self.join(event)

        self.sound_queue.enqueue(self._create_track(audio))

        if not self.first_play:
            await self.play_lock.acquire()
        else:
            self.first_play = False

        await self._play_top_track()

    @Plugin.command(['volume'], 'int')
    async def volume(self, event, volume):
        changed_volume = volume


    def _soundplayer_finished(self):
        self.playing = False
        self.play_lock.release()

    async def _play_top_track(self):
        if self.playing or self.sound_queue.size() <= 0:
            return

        self.playing = True
        player = await self._get_player(self.voice, self.sound_queue.dequeue())
        player.volume = self.volume
        player.start()

    async def _get_player(self, vc, track):
        if vc is None or track is None:
            return None

        player = vc.create_ffmpeg_player(track.get_source(), after=self._soundplayer_finished)

        #if not track.is_link():
        #else:
        #player = await vc.create_ytdl_player(track.get_source(), after=self._soundplayer_finished)
        return player

    def _create_track(self, src):
        #is_link = False

        #if src.startswith('https://') or src.startswith('http://') or src.startswith('www.'):
        #    is_link = True

        #if not is_link:
        src = SoundPlayer._create_path(src, self._CLIPS_DIR, self.path_cache)
        return Track(src, False)

    @staticmethod
    def _create_path(audio, clip_base, path_cache):
        if audio is None or clip_base is None or path_cache is None:
            return

        if path_cache.get(audio) is not None:
            return path_cache.get(audio)

        audio_path = None

        for file in os.listdir(clip_base):
            if os.path.isdir(os.path.join(clip_base, file)):
                if f'{audio}.mp3' in os.listdir(os.path.join(clip_base, file)):
                    audio_path = os.path.join(clip_base, file, f'{audio}.mp3')
                    break

        if audio_path is not None:
            path_cache.insert(audio, audio_path)

        return audio_path
