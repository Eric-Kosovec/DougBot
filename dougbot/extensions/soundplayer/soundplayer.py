import asyncio
import os
import sys
import typing

import discord
from discord.ext import commands

from dougbot.extensions.soundplayer.error import TrackNotExistError
from dougbot.extensions.soundplayer.supportedformats import PLAYER_FILE_TYPES
from dougbot.extensions.soundplayer.track import Track
from dougbot.util.cache import LRUCache


class SoundPlayer(commands.Cog):
    _CLIPS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'res', 'audio')

    def __init__(self, bot):
        self.bot = bot
        self._path_cache = LRUCache(15)
        self._play_lock = asyncio.Lock()  # Stop multiple threads from being created and playing audio over each other.
        self._notify_done_playing = asyncio.Semaphore(0)  # For notifying thread is done playing clip
        self._voice = None
        self._volume = 1.0

    @commands.command(aliases=['sb'], no_pm=True)
    async def play(self, ctx, times: typing.Optional[int], *, source: str):
        if times is None:
            times = 1

        if not ctx.author.voice or (self._voice and ctx.author.voice.channel.id != self._voice.channel.id):
            return

        # Acquire lock so only one thread will play the clips; otherwise, sounds will interleave.
        await self._play_lock.acquire()

        # Bot needs to join the voice channel.
        if self._voice is None:
            self._voice = await self.bot.join_channel(ctx.author.voice.channel)

        try:
            track = await self._create_track(source)
            if track is None:
                await self.bot.confusion(ctx.message)
                return

            # Begin clip block.
            for _ in range(times):
                await self._play_track(track)
                # Wait until thread is done playing current audio before playing the next in the clip block.
                await self._notify_done_playing.acquire()
        except TrackNotExistError:
            await self.bot.confusion(ctx.message)
        except Exception as e:
            await self.bot.confusion(ctx.message)
            print(f'ERROR: Exception raised in SoundPlayer method play: {e}', file=sys.stderr)
        finally:
            self._play_lock.release()

    # Volume is already a superclass' method, so coder beware.
    @commands.command(name='volume', aliases=['vol'], pass_context=False, no_pm=True)
    async def vol(self, volume: float):
        self._volume = max(0.0, min(100.0, volume)) / 100.0
        if self._voice is not None and self._voice.is_playing():
            self._voice.source.volume = self._volume

    @commands.command(pass_context=False, no_pm=True)
    async def pause(self):
        if self._voice is not None and self._voice.is_playing():
            self._voice.pause()

    @commands.command(pass_context=False, no_pm=True)
    async def resume(self):
        if self._voice is not None and self._voice.is_playing():
            self._voice.resume()

    @commands.command(pass_context=False, no_pm=True)
    async def skip(self):
        if self._voice is not None and self._voice.is_playing():
            self._voice.stop()

    @commands.command()
    async def join(self, ctx):
        if not self._voice and ctx.author.voice:
            self._voice = await self.bot.join_channel(ctx.author.voice.channel)

    # Aliases are additional command names beyond the method name.
    @commands.command(aliases=['stop'], no_pm=True)
    async def leave(self, ctx):
        if ctx.author.voice and self._voice and self._voice.channel.id == ctx.author.voice.channel.id:
            await self._quit_playing()

    async def _quit_playing(self):
        await self._voice.disconnect()
        self._voice = None

    async def _play_track(self, track):
        if track is None or self._voice is None:
            self._notify_done_playing.release()
            return
        audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track.src))
        audio_source.volume = self._volume
        self._voice.play(audio_source, after=self._soundplayer_finished)

    def _soundplayer_finished(self, error):
        _ = error
        try:
            asyncio.run_coroutine_threadsafe(self._unlock_play_lock(), self.bot.loop).result()
        except Exception as e:
            # TODO BETTER HANDLING
            raise e

    async def _unlock_play_lock(self):
        self._notify_done_playing.release()

    async def _create_track(self, source):
        is_link = await self._is_link(source)
        if not is_link:
            source = await self._create_path(source)
        return Track(source, is_link)

    @staticmethod
    async def _is_link(candidate):
        if type(candidate) != str:
            return False
        # Rudimentary link detection
        return candidate.startswith('https://') or candidate.startswith('http://') or candidate.startswith('www.')

    async def _create_path(self, audio):
        if audio is None:
            return None

        audio_path = await self._path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        for dirpath, dirnames, filenames in os.walk(self._CLIPS_DIR):
            for ending in PLAYER_FILE_TYPES:
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
