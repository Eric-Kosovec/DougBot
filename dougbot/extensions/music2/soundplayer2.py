import asyncio
import hashlib
import logging
import os
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import cachetools
import nextcord
import youtube_dl
from cachetools import LRUCache
from nextcord import Interaction
from nextcord import Member
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.ui.button import ButtonStyle
from nextcord.ui.view import View

from dougbot.config import EXTENSION_RESOURCES_DIR
from dougbot.core.bot import DougBot
from dougbot.extensions.common import fileutils
from dougbot.extensions.common import webutils
from dougbot.extensions.common.annotation.miccheck import voice_command
from dougbot.extensions.common.ui.button import DougButton
from dougbot.extensions.music2.soundconsumer import SoundConsumer
from dougbot.extensions.music2.track import Track


class SoundPlayer2(commands.Cog):
    _CLIP_DIR = os.path.join(EXTENSION_RESOURCES_DIR, 'music', 'audio')
    _CACHE_DIR = os.path.join(EXTENSION_RESOURCES_DIR, 'music', 'cache')
    _MAXIMUM_PLAYS = 50
    _logger = logging.getLogger(__file__)

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.loop = self.bot.loop

        self._voice = None
        self._volume = 1.0
        self._order_lock = asyncio.Lock()
        self._thread_pool = ThreadPoolExecutor()
        self._file_to_tracks = defaultdict(lambda: [])
        self._file_to_message = {}
        self._playing_message = None
        self._playing_track = None

        self._sound_consumer = SoundConsumer.instance(bot)
        self._sound_consumer_thread = threading.Thread(target=self._sound_consumer.run, name='Sound Consumer', args=[self._volume], daemon=True)
        self._sound_consumer_thread.start()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def play2(self, ctx, source: str, *, times: str = '1'):
        source, times = await self._custom_parse(source, times)
        times = max(1, min(times, self._MAXIMUM_PLAYS))

        if self._voice is None:
            async with self._order_lock:
                self._voice = await self.bot.join_voice_channel(ctx.message.author.voice.channel)

        track = Track(ctx, source, times)
        self._sound_consumer.enqueue(track)
        asyncio.create_task(self._prepare_track(track))
        await ctx.message.delete(delay=3)

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def pause2(self, ctx):
        if self._voice and self._voice.is_playing():
            self._voice.pause()
        await ctx.message.delete(delay=3)

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def resume2(self, ctx):
        if self._voice and self._voice.is_paused():
            self._voice.resume()
        await ctx.message.delete(delay=3)

    @commands.command(aliases=['next2'])
    @commands.guild_only()
    @voice_command()
    async def skip2(self, ctx):
        if self._voice and self._voice.is_playing():
            self._sound_consumer.skip()
        await ctx.message.delete(delay=3)

    @commands.command(aliases=['stop2'])
    @commands.guild_only()
    @voice_command()
    async def leave2(self, ctx):
        await self._stop_playing()
        await ctx.message.delete(delay=3)

    @commands.command(aliases=['volume2'])
    @commands.guild_only()
    @voice_command()
    async def vol2(self, ctx, volume: float):
        self._volume = max(0.0, min(100.0, volume)) / 100.0

        if self._voice and self._voice.is_playing():
            try:
                # Volume is not important to playing, so this is a non-synchronized attempt at changing volume.
                # Thread might finish with voice source before or as volume is changed.
                self._voice.source.volume = self._volume
            except AttributeError:
                pass

        await ctx.message.delete(delay=3)

    async def on_voice_state_update(self, member: Member, before, after):
        # Bot removed
        if member.id == self.bot.user.id and after.channel is None:
            await self._stop_playing()
            return

        # User left
        if before.channel and (after.channel is None or before.channel.id != after.channel.id):
            voice = await self.bot.voice_in(before.channel)
            # Make sure there are no humans in the voice channel.
            if voice and nextcord.utils.find(lambda m: not m.bot, before.channel.members) is None:
                await self._stop_playing()

    def cog_unload(self):
        self._sound_consumer.kill()
        fileutils.delete_directories(self._CACHE_DIR, True)

    async def _stop_playing(self):
        if self._voice is None:
            return

        self._sound_consumer.stop()
        await self._voice.disconnect()
        self._voice = None
        fileutils.delete_directories(self._CACHE_DIR, True)

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

    @cachetools.cached(cache=LRUCache(20))
    async def _find_path(self, audio):
        return await fileutils.find_file_async(self._CLIP_DIR, audio)

    async def _download_link(self, track):
        dl_path = os.path.join(self._CACHE_DIR, await self._link_hash(track.source))
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
            'log': self._logger,
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
        is_paused = self._voice and self._voice.is_paused()
        play_pause = DougButton(callback=self._play_pause_button, style=ButtonStyle.primary, label='Pause' if is_paused else 'Play')
        skip = DougButton(callback=self._skip_button, style=ButtonStyle.primary, label='Next')
        stop = DougButton(callback=self._stop_button, style=ButtonStyle.danger, label='Stop')
        view = View(timeout=None)
        view.add_item(play_pause)
        view.add_item(stop)
        view.add_item(skip)
        return view

    async def _play_pause_button(self, interaction: Interaction):
        if self._voice and self._voice.is_paused():
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
    async def _custom_parse(source, times):
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


def teardown(_):
    cache_path = os.path.join(EXTENSION_RESOURCES_DIR, 'music', 'cache')
    fileutils.delete_directories(cache_path, True)
