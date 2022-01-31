import asyncio
import hashlib
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import youtube_dl
from nextcord.embeds import Embed
from nextcord.ext import commands
from youtube_search import YoutubeSearch

from dougbot.common import reactions
from dougbot.common.cache import LRUCache
from dougbot.core.bot import DougBot
from dougbot.extensions.common import fileutils
from dougbot.extensions.common import webutils
from dougbot.extensions.common.annotations.miccheck import voice_command
from dougbot.extensions.music.soundconsumer import SoundConsumer
from dougbot.extensions.music.track import Track


class SoundPlayer(commands.Cog):

    _logger = logging.getLogger(__file__)

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.loop = self.bot.loop
        self.bot.event(self.on_voice_state_update)

        self._path_cache = LRUCache(20)
        self._thread_pool = ThreadPoolExecutor()

        self._kv = self.bot.kv_store()
        self._order_lock = asyncio.Lock()  # Keeps order tracks are played in.
        self._volume = 1.0 if 'volume' not in self._kv else self._kv['volume']

        self._resource_path = os.path.join(self.bot.extensions_resource_path(), 'music')
        self._clips_dir = os.path.join(self._resource_path, 'audio')
        self._cache_dir = os.path.join(self._resource_path, 'cache')
        self._last_embed_message = None
        self._url = ''
        self._title = ''
        self._thumbnail = ''
        self._duration_seconds = 0

        self._sound_consumer = SoundConsumer.get_soundconsumer(self.bot, self._volume)
        self._sound_consumer_thread = threading.Thread(target=self._sound_consumer.run, name='Sound_Consumer', daemon=True)
        self._sound_consumer_thread.start()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def play(self, ctx, source: str, *, times: str = '1'):
        source, times = await self._custom_play_parse(source, times)
        if times <= 0:
            await reactions.confusion(ctx.message)
            return

        voice = await self.bot.join_voice_channel(ctx.message.author.voice.channel)
        if voice is None:
            await reactions.confusion(ctx.message)
            return

        # Keep ordering of clips
        async with self._order_lock:
            await self._enqueue_audio(ctx, voice, source, times)

        await asyncio.sleep(3)
        await ctx.message.delete()

    # Searches for a youtube video based on the search terms given and sends the url to the play function
    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def ytplay(self, ctx, *, search_terms: str):
        yt_url = ''
        if await webutils.async_is_link(search_terms):
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
            self._volume = max(0.0, min(100.0, volume)) / 100.0
            if voice.is_playing():
                voice.source.volume = self._volume
            self._kv['volume'] = self._volume
        self._sound_consumer.set_volume(volume)

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
            self._sound_consumer.skip_track()

    @commands.command(aliases=['stop'])
    @commands.guild_only()
    @voice_command()
    async def leave(self, ctx):
        voice = await self.bot.get_voice(ctx.message.author.voice.channel)
        if voice is not None:
            await self._quit_playing(voice)

    async def on_voice_state_update(self, _, before, after):
        if before.channel is not None and (after.channel is None or before.channel.id != after.channel.id):
            voice = await self.bot.get_voice(before.channel)
            # Make sure there are no humans in the voice channel.
            if voice is not None and next(filter(lambda m: not m.bot, before.channel.members), None) is None:
                await self._quit_playing(voice)

    async def _quit_playing(self, voice):
        await self.loop.run_in_executor(self._thread_pool, self._sound_consumer.stop_playing)
        if voice is not None:
            await voice.disconnect()
        async with self._order_lock:
            await self.loop.run_in_executor(self._thread_pool, fileutils.delete_directories, self._cache_dir)

    async def _enqueue_audio(self, ctx, voice, source, times):
        track = await self._create_track(ctx, voice, source, times)
        if track is None:
            await reactions.confusion(ctx.message)
            return
        self._sound_consumer.enqueue(track)

    async def _create_track(self, ctx, voice, source, times):
        is_link = webutils.is_link(source)

        if not is_link:
            track_source = await self._get_path(source)
        else:
            track_source = await self._download_link(ctx, source)

        if track_source is None:
            return None

        return Track(ctx, voice, track_source, is_link, times)

    async def _get_path(self, audio):
        audio_path = await self._path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        audio_path = await fileutils.find_file_async(self._clips_dir, audio)
        if audio_path is not None:
            await self._path_cache.insert(audio, audio_path)
            return audio_path

        return None

    async def _download_link(self, ctx, link):
        dl_path = os.path.join(self._cache_dir, await self._link_hash(link))
        if os.path.exists(dl_path):
            return dl_path

        ytdl_params = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'opus',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'outtmpl': dl_path,
            'logger': self._logger,
            'progress_hooks': [self._progress_hook]
        }
        ytdl = youtube_dl.YoutubeDL(ytdl_params)

        ie_result = await self.bot.loop.run_in_executor(self._thread_pool, ytdl.extract_info, link, False)
        if ie_result is None:
            return None

        self._uploader = ie_result['uploader']
        self._title = ie_result['title']
        self._thumbnail = ie_result['thumbnails'][-1]['url']
        self._duration_seconds = ie_result['duration']

        self._url = link
        self._last_embed_message = await ctx.send(embed=self._link_download_embed(self._title, self._uploader, self._thumbnail, self._url, 0))
        await self.bot.loop.run_in_executor(self._thread_pool, ytdl.extract_info, link)

        return dl_path

    def _progress_hook(self, data):
        if self._last_embed_message is None:
            return
        progress = data['downloaded_bytes'] / data['total_bytes'] * 100
        asyncio.run_coroutine_threadsafe(self._last_embed_message.edit(embed=self._link_download_embed(self._title, self._uploader, self._thumbnail, self._url, int(progress))), self.bot.loop)

    @staticmethod
    def _link_download_embed(title, uploader, thumbnail, url, percentage):
        description_markdown = \
            f'''{uploader}
        
            [{title}]({url})
            '''
        return Embed(title='Downloading', description=description_markdown, color=0xFF0000) \
            .set_image(url=thumbnail) \
            .add_field(name='Progress:', value=f'{percentage}%' if percentage < 100 else 'Playing...')

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
            source = f'{source} {" ".join(times_split[:-1])}'
        except ValueError:
            source = f'{source} {times}'
            times = 1

        return source, times


def setup(bot):
    bot.add_cog(SoundPlayer(bot))


def teardown(bot):
    cache_path = os.path.join(bot.extensions_resource_path(), 'music', 'cache')
    fileutils.delete_directories(cache_path, True)
