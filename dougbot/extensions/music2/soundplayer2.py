import asyncio
import hashlib
import logging
import os
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import youtube_dl
from nextcord import Interaction
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.ui.button import ButtonStyle
from nextcord.ui.view import View

from dougbot.common.data.cache import LRUCache
from dougbot.common.messaging import reactions
from dougbot.core.bot import DougBot
from dougbot.extensions.common import fileutils
from dougbot.extensions.common import webutils
from dougbot.extensions.common.annotation.miccheck import voice_command
from dougbot.extensions.common.ui.dougbutton import DougButton
from dougbot.extensions.music2.soundconsumer import SoundConsumer
from dougbot.extensions.music2.track import Track


class SoundPlayer2(commands.Cog):
    _MAXIMUM_PLAYS = 50

    _logger = logging.getLogger(__file__)

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.loop = self.bot.loop

        self._kv = self.bot.kv_store()
        self._volume = 1.0 if 'volume' not in self._kv else self._kv['volume']
        self._path_cache = LRUCache(20)
        self._order_lock = asyncio.Lock()  # Keeps order tracks are played in.
        self._thread_pool = ThreadPoolExecutor()
        self._file_to_tracks = defaultdict(lambda: [])
        self._file_to_message = {}
        self._voice = None
        self._paused = False
        self._playing_message = None
        self._playing_track = None

        self._resource_path = os.path.join(self.bot.RESOURCES_DIR, 'music')
        self._clips_dir = os.path.join(self._resource_path, 'audio')
        self._cache_dir = os.path.join(self._resource_path, 'cache')

        self._sound_consumer = SoundConsumer.instance(bot, self._playing_callback)
        self._sound_consumer_thread = threading.Thread(target=self._sound_consumer.run, name='Sound Consumer', args=[self._volume], daemon=True)
        self._sound_consumer_thread.start()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def play2(self, ctx, source: str, *, times: str = '1'):
        source, times = await self._custom_play_parse(source, times)
        if times not in range(self._MAXIMUM_PLAYS + 1):
            await reactions.confusion(ctx.message)
            return

        if self._voice is None:
            async with self._order_lock:
                self._voice = await self.bot.join_voice_channel(ctx.message.author.voice.channel)

        track = Track(ctx, self._voice, source, times)
        self._sound_consumer.enqueue(track)
        asyncio.create_task(self._prepare_track(track))
        await ctx.message.delete(delay=3)

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def pause2(self, ctx):
        if self._voice is not None and self._voice.is_playing():
            self._voice.pause()
            self._paused = True
        await ctx.message.delete(delay=3)

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def resume2(self, ctx):
        if self._voice is not None and self._voice.is_paused():
            self._voice.resume()
            self._paused = False
        await ctx.message.delete(delay=3)

    @commands.command(aliases=['next2'])
    @commands.guild_only()
    @voice_command()
    async def skip2(self, ctx):
        if self._voice is not None and self._voice.is_playing():
            self._sound_consumer.skip()
        await ctx.message.delete(delay=3)

    @commands.command(aliases=['stop2'])
    @commands.guild_only()
    @voice_command()
    async def leave2(self, ctx):
        if self._voice is not None:
            self._sound_consumer.stop()
            await self._voice.disconnect()
            self._voice = None
            self._paused = False
            fileutils.delete_directories(self._cache_dir, True)
        await ctx.message.delete(delay=3)

    @commands.command(aliases=['volume2'])
    @commands.guild_only()
    @voice_command()
    async def vol2(self, ctx, volume: float):
        # Volume is not important to playing, so this is a non-synchronized attempt at changing volume.
        # Thread might finish with voice source before or as volume is changed.

        if self._voice is None:
            await ctx.message.delete(delay=3)
            return

        self._volume = max(0.0, min(100.0, volume)) / 100.0

        if self._voice.is_playing():
            try:
                self._voice.source.volume = self._volume
            except AttributeError as _:
                pass
        self._kv['volume'] = self._volume
        await ctx.message.delete(delay=3)

    def cog_unload(self):
        self._sound_consumer.kill()
        fileutils.delete_directories(self._cache_dir, True)

    async def _playing_callback(self, track):
        controls = await self._create_controls_view()
        self._playing_message = await track.ctx.send(embed=self._link_download_embed(track, is_playing=True), view=controls)
        self._playing_track = track

    async def _prepare_track(self, track):
        if await webutils.async_is_link(track.source):
            track.source = await self._download_link(track)
            for waiting_track in self._file_to_tracks[track.source]:
                waiting_track.signal_ready()
            del self._file_to_tracks[track.source]
        else:
            track.source = await self._find_path(track.source)
            track.signal_ready()

    async def _find_path(self, audio):
        audio_path = await self._path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        audio_path = await fileutils.find_file_async(self._clips_dir, audio)
        if audio_path is not None:
            await self._path_cache.insert(audio, audio_path)

        return audio_path

    async def _download_link(self, track):
        dl_path = os.path.join(self._cache_dir, await self._link_hash(track.source))
        if os.path.exists(dl_path):
            self._file_to_tracks[dl_path].append(track)
            return dl_path

        # Already being downloaded
        if dl_path in self._file_to_tracks:
            self._file_to_tracks[dl_path].append(track)
            return dl_path

        self._file_to_tracks[dl_path].append(track)

        ytdl = youtube_dl.YoutubeDL({
            'format': 'bestaudio/best',
            'audioformat': 'opus',
            'extractaudio': True,
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
        })

        info = await self.loop.run_in_executor(self._thread_pool, ytdl.extract_info, track.source, False)
        track.uploader = info['uploader']
        track.title = info['title']
        track.thumbnail = info['thumbnails'][-1]['url']
        track.duration = info['duration']

        self._file_to_message[dl_path] = await track.ctx.send(embed=self._link_download_embed(track), view=self._create_controls_view())

        await self.loop.run_in_executor(self._thread_pool, ytdl.extract_info, track.source)
        asyncio.create_task(self._delete_embed(dl_path))

        return dl_path

    async def _delete_embed(self, dl_path):
        await self._file_to_message[dl_path].delete(delay=2)
        del self._file_to_message[dl_path]

    def _progress_hook(self, data):
        progress = '100%' if '_percent_str' not in data else data['_percent_str'].strip()
        filename = data['filename']
        embed_message = self._file_to_message[filename]
        embed = self._link_download_embed(self._file_to_tracks[filename][0], progress)
        asyncio.run_coroutine_threadsafe(embed_message.edit(embed=embed), self.loop)

    @staticmethod
    def _link_download_embed(track, percentage='0.0%', is_playing=False):
        description_markdown = \
            f'''{track.uploader}
        
            [{track.title}]({track.source})
            '''

        if '100' in percentage or is_playing:
            return Embed(title='Playing' if is_playing else 'Finished', description=description_markdown, color=0xFF0000) \
                .set_image(url=track.thumbnail)
        else:
            return Embed(title='Downloading', description=description_markdown, color=0xFF0000) \
                .set_image(url=track.thumbnail) \
                .add_field(name='Progress:', value=f'{percentage}')

    async def _create_controls_view(self):
        play_pause = DougButton(callback=self._play_pause_button, style=ButtonStyle.primary, label='Pause' if self._paused else 'Play')
        skip = DougButton(callback=self._skip_button, style=ButtonStyle.primary, label='Next')
        stop = DougButton(callback=self._stop_button, style=ButtonStyle.danger, label='Stop')
        view = View(timeout=None)
        view.add_item(play_pause)
        view.add_item(stop)
        view.add_item(skip)
        return view

    async def _play_pause_button(self, interaction: Interaction):
        if self._paused:
            await self.resume2(interaction)
        else:
            await self.pause2(interaction)
        await self._playing_message.edit(embed=self._link_download_embed(self._playing_track, is_playing=True), view=await self._create_controls_view())

    async def _stop_button(self, interaction: Interaction):
        await self.leave2(interaction)

    async def _skip_button(self, interaction: Interaction):
        await self.skip2(interaction)

    @staticmethod
    async def _link_hash(link):
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
    bot.add_cog(SoundPlayer2(bot))
