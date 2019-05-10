import asyncio
import io
import os
import sys
import typing

import discord
import youtube_dl
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
        self._notify_downloaded = asyncio.Semaphore(0)
        self._yt_audio = None
        self._voice = None
        self._volume = 1.0
        self.bot.event(self.on_voice_state_update)

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
    @commands.command(name='volume', aliases=['vol'], no_pm=True)
    async def vol(self, ctx, volume: float):
        self._volume = max(0.0, min(100.0, volume)) / 100.0
        if self._voice is not None and self._voice.is_playing():
            self._voice.source.volume = self._volume

    @commands.command(no_pm=True)
    async def pause(self, ctx):
        if self._voice is not None and self._voice.is_playing():
            self._voice.pause()

    @commands.command(no_pm=True)
    async def resume(self, ctx):
        if self._voice is not None and self._voice.is_playing():
            self._voice.resume()

    @commands.command(no_pm=True)
    async def skip(self, ctx):
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

    async def on_voice_state_update(self, member, before, after):
        if member is None or before is None or after is None or before.channel is None or self._voice is None:
            return
        if (after.channel is not None and before.channel.id == after.channel.id) \
                or (before.channel.id != self._voice.channel.id):
            return
        # Make sure there are no humans in the voice channel.
        if next(filter(lambda m: not m.bot, before.channel.members), None) is None:
            await self._quit_playing()

    async def _quit_playing(self):
        await self._voice.disconnect()
        self._voice = None

    async def _play_track(self, track):
        if track is None or self._voice is None:
            self._notify_done_playing.release()
            return
        self._voice.play(await self._create_audio_source(track), after=self._soundplayer_finished)

    async def _create_audio_source(self, track):
        if not track.is_link:
            base_source = discord.FFmpegPCMAudio(track.src, options='-loglevel quiet')
        else:
            base_source = discord.PCMAudio(await self._download_yt(track.src))
        audio_source = discord.PCMVolumeTransformer(base_source)
        audio_source.volume = self._volume
        return audio_source

    def _ydl_done_hook(self, d):
        try:
            if d['status'] == 'finished':
                audio_path = os.path.join(os.path.dirname(self._CLIPS_DIR), 'tmp', d['filename'])
                print(audio_path)
                with open(audio_path, 'rb') as audio:
                    self._yt_audio = audio.read()
                #os.remove(audio_path)
                self._notify_downloaded.release()
            elif d['status'] == 'error':
                self._yt_audio = None
                self._notify_downloaded.release()
        except Exception:  # Make sure the lock is released upon any problems.
            self._notify_downloaded.release()

    async def _download_yt(self, link):
        if link is None:
            return None

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'cachedir': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self._ydl_done_hook]
        }

        cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(self._CLIPS_DIR), 'tmp'))
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            await self._notify_downloaded
        os.chdir(cwd)

        if self._yt_audio is None:
            return None

        byte_stream = io.BytesIO(self._yt_audio)
        self._yt_audio = None
        return byte_stream

    def _soundplayer_finished(self, error):
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
