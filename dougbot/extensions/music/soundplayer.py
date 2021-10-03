import asyncio
import functools
import hashlib
import os
import threading

from concurrent.futures import ThreadPoolExecutor

import youtube_dl
from youtube_search import YoutubeSearch
from discord.ext import commands

from dougbot.common.cache import LRUCache
from dougbot.core.bot import DougBot
from dougbot.extensions.common.autocorrect import Autocorrect
from dougbot.extensions.common.annotations.miccheck import voice_command
from dougbot.extensions.music.soundconsumer import SoundConsumer
from dougbot.extensions.music.track import Track


class SoundPlayer(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.bot.event(self.on_voice_state_update)

        self.path_cache = LRUCache(20)
        self.threads = ThreadPoolExecutor()

        self.kv = self.bot.kv_store()
        self.order_lock = asyncio.Lock()  # Keeps order tracks are played in.
        self.volume = 1.0 if 'volume' not in self.kv else self.kv['volume']

        self.clips_dir = os.path.join(self.bot.ROOT_DIR, 'resources', 'extensions', 'music', 'audio')
        self.cache_dir = os.path.join(self.bot.ROOT_DIR, 'cache')
        self.autocorrect = Autocorrect(self._clip_names())  # Hack

        self.sound_consumer = SoundConsumer.get_soundconsumer(self.bot, self.volume)
        self.sound_consumer_thread = threading.Thread(target=self.sound_consumer.run, name='Sound_Consumer')
        self.sound_consumer_thread.start()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def play(self, ctx, source: str, *, times: str = '1'):
        source, times = await self._custom_play_parse(source, times)
        if times <= 0:
            await self.bot.confusion(ctx.message)
            return

        voice = await self.bot.join_voice_channel(ctx.message.author.voice.channel)
        if voice is None:
            await self.bot.confusion(ctx.message)
            return

        # TODO EXPLORE CREATING TRACK WHILE WAITING
        # Keep ordering of clips
        async with self.order_lock:
            await self._enqueue_audio(ctx, voice, source, times)

    # Searches for a youtube video based on the search terms given and sends the url to the play function
    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def ytplay(self, ctx, *, search_terms: str):
        yt_url = ''
        if await self._is_link(search_terms):
            yt_url = search_terms
        else:
            results = YoutubeSearch(search_terms, max_results=20).to_dict()
            for i in range(0, len(results)):
                if results[i]['publish_time'] != 0:
                    yt_url = f"https://www.youtube.com{results[i]['url_suffix']}"
                    break
        if len(yt_url) > 0:
            await ctx.send(f'Added {yt_url} to the queue...')
            await self.play(ctx, source=yt_url, times='1')
        else:
            await ctx.send('Could not find track to add.')

    # 'volume' is already a superclass' method, so can't use that method name.
    @commands.command(name='volume', aliases=['vol'])
    @commands.guild_only()
    @voice_command()
    async def vol(self, ctx, volume: float):
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None:
            self.volume = max(0.0, min(100.0, volume)) / 100.0
            if voice.is_playing():
                voice.source.volume = self.volume
            self.kv['volume'] = self.volume
        self.sound_consumer.set_volume(volume)

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

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def skip(self, ctx):
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None and voice.is_playing():
            self.sound_consumer.skip_track()

    @commands.command(aliases=['stop'])
    @commands.guild_only()
    @voice_command()
    async def leave(self, ctx):
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
        await self.bot.loop.run_in_executor(self.threads, self.sound_consumer.stop_playing)
        if voice is not None:
            await voice.disconnect()
        await self._clear_cache()

    async def _clear_cache(self):
        async with self.order_lock:
            task = functools.partial(self._remove_files, self.cache_dir)
            await self.bot.loop.run_in_executor(self.threads, task)

    @staticmethod
    def _remove_files(directory):
        for path, _, files in os.walk(directory):
            for file in files:
                try:
                    os.remove(os.path.join(path, file))
                except Exception as e:
                    raise e

    async def _enqueue_audio(self, ctx, voice, source, times):
        track = await self._create_track(ctx, voice, source, times)
        if track is None:
            await self.bot.confusion(ctx.message)
            return

        self.sound_consumer.enqueue(track)

    async def _create_track(self, ctx, voice, source, times):
        is_link = await self._is_link(source)

        if not is_link:
            source = await self._get_path(source)
            if source is None:  # Could be a typo, try again
                source = self.autocorrect.correct(source)
                source = await self._get_path(source)
        else:
            source = await self._download_link(source)

        if source is None:
            return None

        return Track(ctx, voice, source, is_link, times)

    @staticmethod
    async def _is_link(candidate):
        return candidate.startswith('https://') or candidate.startswith('http://') or candidate.startswith('www.')

    async def _get_path(self, audio):
        audio_path = await self.path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        for path, _, files in os.walk(self.clips_dir):
            for filename in files:
                if audio.lower() == os.path.splitext(filename)[0].lower():
                    audio_path = os.path.join(path, filename)
                    await self.path_cache.insert(audio, audio_path)
                    return audio_path

        return None

    async def _download_link(self, link):
        dl_path = os.path.join(self.cache_dir, await self._link_hash(link))
        if os.path.exists(dl_path):
            return dl_path

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

        task = functools.partial(ytdl.extract_info, link)
        await self.bot.loop.run_in_executor(self.threads, task)

        return dl_path

    @staticmethod
    async def _link_hash(link):
        link = 'yt_' + link
        md5hash = hashlib.new('md5')
        md5hash.update(link.encode('utf-8'))
        return md5hash.hexdigest()

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
        for _, _, filenames in os.walk(self.clips_dir):
            clips.extend([f[:f.rfind('.')] for f in filenames])
        return clips


def setup(bot):
    bot.add_cog(SoundPlayer(bot))
