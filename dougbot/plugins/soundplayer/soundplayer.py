import os
import subprocess
from asyncio.locks import Semaphore
from subprocess import CalledProcessError

from dougbot.plugins.listento import ListenTo
from dougbot.plugins.plugin import Plugin
from dougbot.plugins.soundplayer.track import Track
from dougbot.util.cache import LRUCache
from dougbot.util.queue import Queue


class SoundPlayer(Plugin):

    _CLIPS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _CLIPS_DIR = os.path.join(_CLIPS_DIR, 'res', 'sbsounds')

    SUPPORTED_FILE_TYPES = ['.mp3', '.m4a']

    def __init__(self):
        super().__init__()
        self.path_cache = LRUCache(15)
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

        user_voice_channel = event.author.voice.voice_channel

        # Commander is not in a voice channel, or bot is already in a voice channel on the server
        if user_voice_channel is None or event.bot.voice_client_in(event.server) is not None:
            return

        self.voice = await event.bot.join_channel(user_voice_channel)
        self.player = None
        self.playing = False
        self.first_play = True
        self.play_lock = Semaphore(0, loop=event.event_loop)
        self.sound_queue.clear()

    @Plugin.command('leave')
    async def leave(self, event):
        if event is None or event.channel.is_private:
            return

        user_voice_channel = event.author.voice.voice_channel

        # User is not in a voice channel
        if user_voice_channel is None:
            return

        bot_voice_client = event.bot.voice_client_in(event.server)

        # Bot not in a voice channel or user is not in the same voice channel
        if bot_voice_client is None or bot_voice_client.channel != user_voice_channel:
            return

        await self._reset_state()

        await event.bot.leave_channel(bot_voice_client.channel)

    @Plugin.command(['sb', 'play'], str)
    async def play(self, event, audio):
        if event is None or audio is None:
            return

        await self.join(event)

        self.sound_queue.enqueue(self._create_track(audio))

        '''
        A Semaphore must be used due to a race condition on the 'playing' boolean variable and to get a non-async 
        callback to play nice with asyncs.
        Playing a web link or sound file runs in a separate thread than ours, so the callback method 
        '_soundplayer_finished' gets called and ran in a separate thread. This method sets playing to False, and 
        it previously allowed playing of the next track in the queue. This caused multiple tracks to be played at once, 
        as before one thread could set 'playing' to True, the other saw it as False.
        '''
        if not self.first_play:
            await self.play_lock.acquire()
        else:
            self.first_play = False

        await self._play_top_track()

    @Plugin.command('volume', int)
    async def volume(self, event, volume):
        self.volume = max(0.0, min(100.0, float(volume))) / 100.0
        # Might bring a race condition, so just ignore volume change if this occurs. Doesn't matter in our context.
        try:
            if self.player is not None:
                self.player.volume = self.volume
        except AttributeError:
            pass

    @Plugin.command('stop')
    async def stop(self, event):
        self.sound_queue.clear()
        try:
            if self.player is not None:
                self.player.stop()
        except AttributeError:
            pass
        finally:
            await self.leave(event)

    @Plugin.command('pause')
    async def pause(self):
        try:
            if self.player is not None:
                self.player.pause()
        except AttributeError:
            pass

    @Plugin.command('resume')
    async def resume(self):
        try:
            if self.player is not None:
                self.player.resume()
        except AttributeError:
            pass

    @Plugin.command('skip')
    async def skip(self, event):
        try:
            if self.player is not None:
                self.player.stop()
        except AttributeError:
            pass

    @Plugin.command(['list', 'clips'])
    async def clipslist(self, event):
        clips = []

        # TODO RECURSIVE WITH ALL FOLDERS/SUBFOLDERS

        for file in os.listdir(self._CLIPS_DIR):
            if os.path.isdir(os.path.join(self._CLIPS_DIR, file)):
                for track in os.listdir(os.path.join(self._CLIPS_DIR, file)):
                    if self._is_audio_track(track):
                        clips.append(track[:track.rfind('.')])
            elif self._is_audio_track(file):
                clips.append(file[:file.rfind('.')])

        enter = ''
        clip_message = ''

        for clip in clips:
            clip_message += enter + clip
            enter = '\n'

        await event.bot.send_message(event.channel, clip_message)

    def _is_audio_track(self, candidate):
        if type(candidate) != str:
            return False
        for ending in self.SUPPORTED_FILE_TYPES:
            if candidate.endswith(ending):
                return True
        return False

    @Plugin.command('refresh')
    async def refresh_clips(self, event):
        cwd = os.getcwd()
        os.chdir('../..')
        try:
            subprocess.check_call(['git', 'checkout', 'master', 'dougbot/res/sbsounds'])
        except CalledProcessError:
            await event.bot.confusion(event.message)
        finally:
            os.chdir(cwd)

    @Plugin.listen(ListenTo.ON_VOICE_STATE_UPDATE)
    async def _check_for_users_left(self, event, before, after):
        if event is None or before is None or after is None or self.voice is None:
            return

        if before.voice_channel.id == after.voice_channel.id:
            return

        if before.voice_channel.id == self.voice.channel.id and len(self.voice.channel.voice_members) <= 1:
            await self._reset_state()
            await event.bot.leave_channel(before.voice_channel)

    async def _reset_state(self):
        self.sound_queue.clear()

        if self.play_lock is not None:
            self.play_lock.release()
            self.play_lock = None

        if self.player is not None:
            self.player.stop()

        if self.voice is not None:
            await self.voice.disconnect()
            self.voice = None

        self.player = None
        self.playing = False

    def _soundplayer_finished(self):
        self.playing = False
        if self.play_lock is not None:
            self.play_lock.release()

    async def _play_top_track(self):
        if self.playing or len(self.sound_queue) <= 0:
            return

        self.playing = True
        self.player = await self._get_player(self.voice, self.sound_queue.dequeue())
        self.player.volume = self.volume
        self.player.start()

    async def _get_player(self, vc, track):
        if vc is None or track is None:
            return None

        if not track.is_link:
            player = vc.create_ffmpeg_player(track.src, after=self._soundplayer_finished)
        else:
            player = await vc.create_ytdl_player(track.src, after=self._soundplayer_finished)

        return player

    def _create_track(self, src):
        is_link = False

        if src.startswith('https://') or src.startswith('http://') or src.startswith('www.'):
            is_link = True

        if not is_link:
            src = self._create_path(src, self._CLIPS_DIR, self.path_cache)

        return Track(src, is_link)

    def _create_path(self, audio, clip_base, path_cache):
        if audio is None or clip_base is None or path_cache is None:
            return

        if path_cache.get(audio) is not None:
            return path_cache.get(audio)

        audio_path = None

        for ending in self.SUPPORTED_FILE_TYPES:
            if f'{audio}{ending}' in os.listdir(clip_base):
                audio_path = os.path.join(clip_base, f'{audio}{ending}')
                path_cache.insert(audio, audio_path)
                return audio_path

        for file in os.listdir(clip_base):
            if os.path.isdir(os.path.join(clip_base, file)):
                for ending in self.SUPPORTED_FILE_TYPES:
                    if f'{audio}{ending}' in os.listdir(os.path.join(clip_base, file)):
                        audio_path = os.path.join(clip_base, file, f'{audio}{ending}')
                        break

        if audio_path is not None:
            path_cache.insert(audio, audio_path)

        return audio_path
