import os
import subprocess
from asyncio.locks import Semaphore
from subprocess import CalledProcessError

from dougbot.plugins.plugin import Plugin
from dougbot.plugins.soundplayer.track import Track
from dougbot.plugins.util.join import bot_join, bot_leave
from dougbot.util.cache import LRUCache
from dougbot.util.queue import Queue


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
        self.player = None
        self.voice = None
        self.volume = 1.0

    @Plugin.command('join')
    async def join(self, event):
        if event is None or event.channel.is_private or self.voice is not None:
            return

        self.voice = await bot_join(event)
        self.player = None
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

        # TODO CLEANUP

        self.play_lock.release()
        self.play_lock = None

        await self.voice.disconnect()
        self.voice = None

        if self.player is not None:
            self.player.stop()

        self.player = None
        self.playing = False

        self.sound_queue.clear()

        await bot_leave(event)

    @Plugin.command(['sb', 'play'], str)
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

    @Plugin.command(['volume'], int)
    async def volume(self, event, volume):
        self.volume = max(0.0, min(100.0, float(volume))) / 100.0
        try:  # TODO MIGHT BRING A RACE CONDITION, SO JUST IGNORE VOLUME CHANGE IF THIS HAPPENS
            if self.player is not None:
                self.player.volume = self.volume
        except AttributeError:
            pass

    @Plugin.command(['stop'])
    async def stop(self, event):
        self.sound_queue.clear()
        if self.player is not None:
            self.player.stop()
        await self.leave(event)

    @Plugin.command(['pause'])
    async def pause(self):
        if self.player is not None:
            self.player.pause()

    @Plugin.command(['resume'])
    async def resume(self):
        if self.player is not None:
            self.player.resume()

    @Plugin.command(['skip'])
    async def skip(self, event):
        if self.player is not None:
            self.player.stop()

    @Plugin.command(['list', 'clips'])
    async def clipslist(self, event):
        clips = []

        # TODO RECURSIVE WITH ALL FOLDERS/SUBFOLDERS

        for file in os.listdir(self._CLIPS_DIR):
            if os.path.isdir(os.path.join(self._CLIPS_DIR, file)):
                for track in os.listdir(os.path.join(self._CLIPS_DIR, file)):
                    if track.endswith('.mp3'):
                        clips.append(track[:-len('.mp3')])
            elif file.endswith('.mp3'):
                clips.append(file[:-len('.mp3')])

        enter = ''
        clip_message = ''

        for clip in clips:
            clip_message += enter + clip
            enter = '\n'

        await event.reply(clip_message)

    @Plugin.command(['refresh'])
    async def refresh_clips(self, event):
        cwd = os.getcwd()
        os.chdir('../..')
        try:
            subprocess.check_call(['git', 'checkout', 'master', 'dougbot/res/sbsounds'])
        except CalledProcessError:
            await event.bot.confusion(event.message)
        finally:
            os.chdir(cwd)

    def _soundplayer_finished(self):
        self.playing = False
        self.play_lock.release()

    async def _play_top_track(self):
        if self.playing or self.sound_queue.size() <= 0:
            return

        self.playing = True
        self.player = await self._get_player(self.voice, self.sound_queue.dequeue())
        self.player.volume = self.volume
        self.player.start()

    async def _get_player(self, vc, track):
        if vc is None or track is None:
            return None

        if not track.is_link():
            player = vc.create_ffmpeg_player(track.get_source(), after=self._soundplayer_finished)
        else:
            player = await vc.create_ytdl_player(track.get_source(), after=self._soundplayer_finished)

        return player

    def _create_track(self, src):
        is_link = False

        if src.startswith('https://') or src.startswith('http://') or src.startswith('www.'):
            is_link = True

        if not is_link:
            src = SoundPlayer._create_path(src, self._CLIPS_DIR, self.path_cache)

        return Track(src, is_link)

    @staticmethod
    def _create_path(audio, clip_base, path_cache):
        if audio is None or clip_base is None or path_cache is None:
            return

        if path_cache.get(audio) is not None:
            return path_cache.get(audio)

        audio_path = None

        if f'{audio}.mp3' in os.listdir(clip_base):
            audio_path = os.path.join(clip_base, f'{audio}.mp3')
            path_cache.insert(audio, audio_path)
            return audio_path

        for file in os.listdir(clip_base):
            if os.path.isdir(os.path.join(clip_base, file)):
                if f'{audio}.mp3' in os.listdir(os.path.join(clip_base, file)):
                    audio_path = os.path.join(clip_base, file, f'{audio}.mp3')
                    break

        if audio_path is not None:
            path_cache.insert(audio, audio_path)

        return audio_path
