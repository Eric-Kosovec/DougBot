import asyncio
import os
import sys

from discord.ext import commands

from dougbot.extensions.soundplayer.error import TrackNotExistError
from dougbot.extensions.soundplayer.track import Track
from dougbot.util.cache import LRUCache


class SoundPlayer:
    _CLIPS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'res', 'audio')

    SUPPORTED_FILE_TYPES = ['.mp1', '.mp2', '.mp3', '.mp4', '.m4a', '.3gp', '.aac', '.flac', '.wav', '.aif']

    def __init__(self, bot):
        self.bot = bot
        self._path_cache = LRUCache(15)
        self._play_lock = asyncio.Lock()  # TODO WRITE WHAT FOR
        self._notify_done_playing = asyncio.Semaphore(0)  # For notifying thread is done playing clip
        self._volume = 1.0
        self._player = None
        self._voice = None

    # Context (CTX) variables: 'args', 'bot', 'cog',
    # 'command', 'invoke', 'invoked_subcommand',
    # 'invoked_with', 'kwargs', 'message', 'prefix',
    # 'subcommand_passed', 'view'
    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        # Commander is not in a voice channel, or bot is already in a voice channel on the server
        if ctx.message.author.voice is None or self.bot.voice_client_in(ctx.message.server) is not None:
            return
        self._voice = await self.bot.join_channel(ctx.message.author.voice.voice_channel)

    # Aliases are additional command names beyond the method name.
    @commands.command(aliases=['stop'], pass_context=True, no_pm=True)
    async def leave(self, ctx):
        if ctx.message.author.voice is None:
            return
        bot_voice_client = self.bot.voice_client_in(ctx.message.server)
        # Bot not in a voice channel or user is not in the same voice channel
        if bot_voice_client is None or bot_voice_client.channel != ctx.message.author.voice.voice_channel:
            return
        await self._quit_playing(bot_voice_client.channel)

    # Synchronized code
    @commands.command(aliases=['sb'], pass_context=True, no_pm=True)
    async def play(self, ctx, audio: str, times: int = 1):
        if times <= 0:
            await self.bot.confusion(ctx.message)
            return

        if self._voice is None:
            # Note: Cannot call other commands; e.g., cannot just call the join command here.
            self._voice = await self.bot.join_channel(ctx.message.author.voice.voice_channel)

        # Acquire lock so only one thread will play the clips; otherwise, sounds will interleave.
        # This solution at the moment has the possibility of sounds not playing in the order they were
        # commanded in, stemming from the use of the below lock, as the awaiters on the lock may not necessarily
        # acquire in order of arrival. A correct solution should not depend upon the scheduling of the underlying
        # system. To be properly implemented later.
        await self._play_lock.acquire()

        try:
            track = await self._create_track(audio)
            if track is None:
                await self.bot.confusion(ctx.message)
                return

            for _ in range(times):
                await self._play_track(track)
                await self._notify_done_playing.acquire()
        except TrackNotExistError:
            await self.bot.confusion(ctx.message)
        except Exception as e:
            await self.bot.confusion(ctx.message)
            print(f'ERROR: Exception raised in SoundPlayer method play: {e}', file=sys.stderr)
        finally:
            self._play_lock.release()

    def _soundplayer_finished(self):
        try:
            asyncio.run_coroutine_threadsafe(self._unlock_play_lock(), self.bot.loop).result()
        except Exception as e:
            # TODO BETTER HANDLING
            raise e

    async def _unlock_play_lock(self):
        self._notify_done_playing.release()

    # Volume is already a superclass' method, so coder beware.
    @commands.command(name='volume', aliases=['vol'], no_pm=True)
    async def vol(self, volume: float):
        self._volume = max(0.0, min(100.0, volume)) / 100.0
        if self._player is not None:
            self._player.volume = self._volume

    @commands.command(no_pm=True)
    async def pause(self):
        if self._player is not None:
            self._player.pause()

    @commands.command(no_pm=True)
    async def resume(self):
        if self._player is not None:
            self._player.resume()

    @commands.command(no_pm=True)
    async def skip(self):
        if self._player is not None:
            self._player.stop()

    async def _quit_playing(self, channel):
        # TODO ANY SYNCHRONIZATION ISSUES? - FIRST GLANCE NO, BUT LOOK LATER
        if self._player is not None:
            self._player.stop()
            self._player = None

        if self._voice is not None:
            tmp = self._voice
            self._voice = None  # Null out the field before giving away control through await.
            await tmp.disconnect()

        await self.bot.leave_channel(channel)

    async def _play_track(self, track):
        if track is None or self._voice is None:
            self._notify_done_playing.release()
            return
        self._player = await self._get_player(self._voice, track)
        self._player.volume = self._volume
        self._player.start()

    # Listeners

    # Listening for events will be registered just by making a method with prefix 'on_voice.'
    async def on_voice_state_update(self, before, after):
        if before is None or after is None or self._voice is None:
            return

        if before.voice_channel is None or before.voice_channel == after.voice_channel:
            return

        if before.voice_channel == self._voice.channel and not await self._has_human_members(self._voice.channel):
            await self._quit_playing(before.voice_channel)

    # Utility Methods

    @staticmethod
    async def _has_human_members(channel):
        # If there is a hit of an item with bot variable being false, then there is a human in the channel.
        return next(filter(lambda m: not m.bot, channel.voice_members), None) is not None

    @staticmethod
    async def _is_link(candidate):
        if type(candidate) != str:
            return False
        # Rudimentary link detection
        return candidate.startswith('https://') or candidate.startswith('http://') or candidate.startswith('www.')

    async def _get_player(self, vc, track):
        if vc is None or track is None:
            return None
        callback = self._soundplayer_finished
        if not track.is_link:
            player = vc.create_ffmpeg_player(track.src, options='-loglevel quiet', after=callback)
        else:
            player = await vc.create_ytdl_player(track.src, after=callback)
        return player

    async def _create_track(self, src):
        is_link = await self._is_link(src)
        if not is_link:
            src = await self._create_path(src)
        return Track(src, is_link)

    async def _create_path(self, audio):
        if audio is None:
            return None

        audio_path = await self._path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        for dirpath, dirnames, filenames in os.walk(self._CLIPS_DIR):
            for ending in self.SUPPORTED_FILE_TYPES:
                if f'{audio}{ending}'.lower() in self._lowercase_gen(filenames):
                    audio_path = os.path.join(dirpath, f'{audio}{ending}')
                    await self._path_cache.insert(audio, audio_path)
                    return audio_path

        return None

    @staticmethod
    def _lowercase_gen(strings):
        for string in strings:
            yield string.lower()


def setup(bot):
    bot.add_cog(SoundPlayer(bot))
