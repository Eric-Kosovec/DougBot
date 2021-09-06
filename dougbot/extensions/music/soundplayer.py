import asyncio
import functools
import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import discord
import youtube_dl
from discord.ext import commands

from dougbot.common.cache import LRUCache
from dougbot.core.bot import DougBot
from dougbot.extensions.common.autocorrect import Autocorrect
from dougbot.extensions.common.miccheck import voice_command
from dougbot.extensions.music.error import TrackNotExistError
from dougbot.extensions.music.supportedformats import PLAYER_FILE_TYPES
from dougbot.extensions.music.track import Track


class SoundPlayer(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.bot.event(self.on_voice_state_update)
        self._threads = ThreadPoolExecutor()
        self._clips_dir = os.path.join(self.bot.ROOT_DIR, 'resources', 'audio')
        self._cache_dir = os.path.join(self.bot.ROOT_DIR, 'cache')
        self._autocorrect = Autocorrect(self._clip_names())  # Hack until rewrite
        self._kv = self.bot.kv_store()
        self._path_cache = LRUCache(20)
        self._play_lock = asyncio.Lock()  # Stop multiple threads from being created and playing audio over each other.
        self._notify_done_playing = asyncio.Semaphore(0)  # For notifying thread is done playing clip
        self._links_to_play = 0
        self._volume = 1.0 if not self._kv.contains('volume') else self._kv['volume']
        self._skip = False

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def play(self, ctx, source: str, *, times: str = '1'):
        source, times = await self._custom_play_parse(source, times)
        if times <= 0:
            await self.bot.confusion(ctx.message)
            return

        source = self._autocorrect.correct(source)

        # Acquire lock so only one thread will play the clips; otherwise, sounds will interleave.
        await self._play_lock.acquire()
        try:
            voice = await self.bot.join_voice_channel(ctx.message.author.voice.channel)
            if voice is None:
                self._play_lock.release()
                await self.bot.confusion(ctx.message)
                return

            track = await self._create_track(source)
            if track is None:
                await self.bot.confusion(ctx.message)
                return

            # Track how many links will be played, for clearing cache.
            if track.is_link:
                self._links_to_play += times

            # Begin clip block.
            self._skip = False
            for _ in range(times):
                if self._skip:
                    break
                voice.play(await self._create_audio_source(track), after=self._finished)
                # Wait until thread is done playing current audio before playing the next in the clip block.
                await self._notify_done_playing.acquire()
            if track.is_link:
                self._links_to_play -= times
        except TrackNotExistError:
            await self.bot.confusion(ctx.message)
        except Exception as e:
            await self.bot.confusion(ctx.message)
            print(f'ERROR: Exception raised in SoundPlayer method play: {e}', file=sys.stderr)
        finally:
            self._play_lock.release()

    # Volume is already a superclass' method, so beware.
    @commands.command(name='volume', aliases=['vol'])
    @commands.guild_only()
    @voice_command()
    async def vol(self, ctx, volume: float):
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None:
            self._volume = max(0.0, min(100.0, volume)) / 100.0
            if voice.is_playing():
                voice.source.volume = self._volume
            self._kv['volume'] = self._volume

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def pause(self, ctx):
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None and voice.is_playing():
            voice.pause()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def resume(self, ctx):
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None and voice.is_paused():
            voice.resume()

    @commands.command(aliases=['next'])
    @commands.guild_only()
    @voice_command()
    async def skip(self, ctx):
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None and voice.is_playing():
            voice.stop()
            self._skip = True

    @commands.command(aliases=['stop'])
    @commands.guild_only()
    @voice_command()
    async def leave(self, ctx):
        # TODO MIGHT CAUSE AN ISSUE IF MULTIPLE SOUNDS ARE "QUEUED" UP, AS ONCE THE BLOCK IS SKIPPED AND VOICE ->
        # TODO DISCONNECTED, IT WILL REJOIN TO PLAY THE NEXT BLOCK OF SOUNDS.
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None:
            await self._quit_playing(voice)

    async def on_voice_state_update(self, member, before, after):
        if member is None or before is None or after is None or before.channel is None:
            return
        if (after.channel is not None and before.channel.id == after.channel.id) \
                or not await self.bot.in_voice_channel(before.channel):
            return
        # Make sure there are no humans in the voice channel.
        if next(filter(lambda m: not m.bot, before.channel.members), None) is None:
            voice = await self.bot.get_voice(before.channel)
            await self._quit_playing(voice)

    async def _quit_playing(self, voice):
        self._skip = True
        self._links_to_play = 0
        if voice is not None:
            voice.stop()
            await voice.disconnect()
        await self._clear_cache()

    async def _create_audio_source(self, track):
        audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track.src, options='-loglevel quiet'))
        audio_source.volume = self._volume
        return audio_source

    def _finished(self, error):
        if error is not None:
            print(f'ERROR: SoundPlayer finished error: {error}', file=sys.stderr)
        self._notify_done_playing.release()

    async def _create_track(self, source):
        is_link = await self._is_link(source)
        if not is_link:
            source = await self._create_path(source)
        else:
            source = await self._download_link(source)
        return Track(source, is_link) if source is not None else None

    @staticmethod
    async def _is_link(candidate):
        # Rudimentary link detection
        return type(candidate) == str and (candidate.startswith('https://') or candidate.startswith('http://')
                                           or candidate.startswith('www.'))

    async def _create_path(self, audio):
        if audio is None:
            return None

        audio_path = await self._path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        for path, _, files in os.walk(self._clips_dir):
            for ending in PLAYER_FILE_TYPES:
                if f'{audio}{ending}'.lower() in self._lowercase_gen(files):
                    audio_path = os.path.join(path, f'{audio}{ending}')
                    await self._path_cache.insert(audio, audio_path)
                    return audio_path

        return None

    @staticmethod
    def _lowercase_gen(strings):
        for string in strings:
            yield string.lower()

    async def _download_link(self, link):
        if link is None:
            return None

        dl_path = os.path.join(self._cache_dir, await self._link_hash(link))
        ytdl_params = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'opus',
            'restrictfilenames': True,
            'noplaylist': False,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'outtmpl': dl_path
        }
        ytdl = youtube_dl.YoutubeDL(ytdl_params)

        if not os.path.exists(dl_path):
            task = functools.partial(ytdl.extract_info, link)
            await self.bot.loop.run_in_executor(self._threads, task)

        return dl_path

    async def _clear_cache(self):
        async with self._play_lock:
            if self._links_to_play > 0:
                return
            task = functools.partial(self._remove_files, self._cache_dir)
            await self.bot.loop.run_in_executor(self._threads, task)

    @staticmethod
    async def _link_hash(link):
        if link is None:
            return None
        link = 'yt_' + link
        md5hash = hashlib.new('md5')
        md5hash.update(link.encode('utf-8'))
        return md5hash.hexdigest()

    @staticmethod
    def _remove_files(directory):
        for path, _, files in os.walk(directory):
            for file in files:
                try:
                    os.remove(os.path.join(path, file))
                except Exception as e:
                    print(f'Failed to remove sound player cache file(s): {e}', file=sys.stderr)

    @staticmethod
    async def _custom_play_parse(source, times):
        try:
            times_split = times.split()
            times = int(times_split[-1])
            source = f'{source} {" ".join(times_split[:-1])}'.strip()
        except ValueError:
            source = f'{source} {times}'.strip()
            times = 1

        return source, times

    def _clip_names(self):
        clips = []
        for _, _, filenames in os.walk(self._clips_dir):
            clips.extend([f[:f.rfind('.')] for f in filenames if self._is_audio_track(f)])
        return clips

    @staticmethod
    def _is_audio_track(filename):
        return type(filename) == str and '.' in filename and filename[filename.rfind('.'):] in PLAYER_FILE_TYPES


def setup(bot):
    bot.add_cog(SoundPlayer(bot))
