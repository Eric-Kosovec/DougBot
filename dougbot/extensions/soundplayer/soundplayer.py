import asyncio
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
        self._notify_downloaded = asyncio.Semaphore(0)  # For notifying YouTube video is done downloading.
        self._link_audio_path = None
        self._curr_track = None
        self._voice = None
        self._volume = 1.0
        self._skip = False
        self.bot.event(self.on_voice_state_update)

    @commands.command(aliases=['sb'])
    @commands.guild_only()
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

        self._skip = False

        try:
            track = await self._create_track(source)
            if track is None:
                await self.bot.confusion(ctx.message)
                self._play_lock.release()
                return

            self._curr_track = track

            # Begin clip block.
            for i in range(times):
                if self._skip:
                    break
                await self._play_track(track)
                # Wait until thread is done playing current audio before playing the next in the clip block.
                await self._notify_done_playing.acquire()

            self._skip = False

            if self._curr_track is not None and self._curr_track.is_link:
                os.remove(track.src)

            self._curr_track = None
            self._play_lock.release()
        except TrackNotExistError:
            await self.bot.confusion(ctx.message)
            self._play_lock.release()
        except Exception as e:
            await self.bot.confusion(ctx.message)
            print(f'ERROR: Exception raised in SoundPlayer method play: {e}', file=sys.stderr)
            self._play_lock.release()

    # Volume is already a superclass' method, so beware.
    @commands.command(name='volume', aliases=['vol'])
    @commands.guild_only()
    async def vol(self, ctx, volume: float):
        self._volume = max(0.0, min(100.0, volume)) / 100.0
        if self._voice is not None and self._voice.is_playing():
            self._voice.source.volume = self._volume

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        if self._voice is not None and self._voice.is_playing():
            self._voice.pause()

    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        if self._voice is not None and self._voice.is_playing():
            self._voice.resume()

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        if self._voice is not None and self._voice.is_playing():
            self._skip = True
            self._voice.stop()

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx, *, channel=None):
        if self._voice is not None or (channel is None and ctx.author.voice is None):
            return

        voice_channel = None
        if channel is not None:
            for vc in ctx.message.guild.voice_channels:
                if vc.name.lower() == channel.lower():
                    voice_channel = vc
                    break
            if voice_channel is None:
                await self.bot.confusion(ctx.message)
                return

        if channel is None and ctx.author.voice is not None:
            voice_channel = ctx.author.voice.channel

        self._voice = await self.bot.join_channel(voice_channel)

    # Aliases are additional command names beyond the method name.
    @commands.command(aliases=['stop'])
    @commands.guild_only()
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
        self._skip = True
        await self._voice.disconnect()
        self._voice = None
        # Clear track's files.
        if self._curr_track is not None and self._curr_track.is_link:
            os.remove(self._curr_track.src)
        self._curr_track = None

    async def _play_track(self, track):
        if track is None or self._voice is None:
            self._notify_done_playing.release()
            return
        self._voice.play(await self._create_audio_source(track), after=self._soundplayer_finished)

    async def _create_audio_source(self, track):
        audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track.src, options='-loglevel quiet'))
        audio_source.volume = self._volume
        return audio_source

    def _ydl_done_hook(self, d):
        try:
            if d['status'] == 'finished':
                filename = f"{d['filename'][:d['filename'].rfind('.')]}.mp3"
                self._link_audio_path = os.path.join(os.path.dirname(self._CLIPS_DIR), 'tmp', filename)
                self._notify_downloaded.release()
            elif d['status'] == 'error':
                self._link_audio_path = None
                self._notify_downloaded.release()
        except Exception:  # Make sure the lock is released upon any problems.
            self._notify_downloaded.release()

    async def _download_link(self, link):
        if link is None:
            return None

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
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

        if self._link_audio_path is None:
            return None

        tmp = self._link_audio_path
        self._link_audio_path = None
        return tmp

    def _soundplayer_finished(self, error):
        _ = error
        try:
            asyncio.run_coroutine_threadsafe(self._unlock_play_lock(), self.bot.loop).result()
        except Exception as e:
            asyncio.run_coroutine_threadsafe(self._quit_playing(), self.bot.loop).result()
            raise e

    async def _unlock_play_lock(self):
        self._notify_done_playing.release()

    async def _create_track(self, source):
        is_link = await self._is_link(source)
        if not is_link:
            source = await self._create_path(source)
        else:
            source = await self._download_link(source)
        if source is None:
            return None
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
