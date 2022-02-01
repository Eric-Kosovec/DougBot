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

from dougbot.common import reactions
from dougbot.common.cache import LRUCache
from dougbot.core.bot import DougBot
from dougbot.extensions.common import fileutils
from dougbot.extensions.common import webutils
from dougbot.extensions.common.annotations.miccheck import voice_command
from dougbot.extensions.common.ui.dougbutton import DougButton
from dougbot.extensions.music2.soundconsumer import SoundConsumer
from dougbot.extensions.music2.track import Track


class SoundPlayer2(commands.Cog):

    _logger = logging.getLogger(__file__)

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.loop = self.bot.loop

        self._voice = None
        self._path_cache = LRUCache(20)
        self._order_lock = asyncio.Lock()  # Keeps order tracks are played in.
        self._thread_pool = ThreadPoolExecutor()
        self._file_to_tracks = defaultdict(lambda: [])
        self._file_to_message = {}

        self._resource_path = os.path.join(self.bot.extensions_resource_path(), 'music')
        self._clips_dir = os.path.join(self._resource_path, 'audio')
        self._cache_dir = os.path.join(self._resource_path, 'cache')

        self._sound_consumer = SoundConsumer.instance(bot)
        self._sound_consumer_thread = threading.Thread(target=self._sound_consumer.run, name='Sound Consumer', daemon=True)
        self._sound_consumer_thread.start()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def play2(self, ctx, source: str, *, times: str = '1'):
        source, times = await self._custom_play_parse(source, times)
        if times not in range(31):
            await reactions.confusion(ctx.message)
            return

        if self._voice is None:
            async with self._order_lock:
                self._voice = await self.bot.join_voice_channel(ctx.message.author.voice.channel)

        track = Track(ctx, self._voice, source, times)
        self._sound_consumer.enqueue(track)
        asyncio.create_task(self._prepare_track(track))

        await asyncio.sleep(3)
        await ctx.message.delete()

    def cog_unload(self):
        self._sound_consumer.stop()
        fileutils.delete_directories(self._cache_dir, True)

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
        # await self._file_to_message[dl_path].delete()
        del self._file_to_message[dl_path]

    def _progress_hook(self, data):
        progress = '100%' if '_percent_str' not in data else data['_percent_str'].strip()
        filename = data['filename']
        embed_message = self._file_to_message[filename]
        embed = self._link_download_embed(self._file_to_tracks[filename][0], progress)
        asyncio.run_coroutine_threadsafe(embed_message.edit(embed=embed, view=self._create_controls_view()), self.loop)

    @staticmethod
    def _link_download_embed(track, percentage='0.0%'):
        description_markdown = \
            f'''{track.uploader}
        
            [{track.title}]({track.source})
            '''

        if '100' in percentage:
            return Embed(title='Playing', description=description_markdown, color=0xFF0000)\
                .set_image(url=track.thumbnail)
        else:
            return Embed(title='Downloading', description=description_markdown, color=0xFF0000)\
                .set_image(url=track.thumbnail)\
                .add_field(name='Progress:', value=f'{percentage}')

    def _create_controls_view(self):
        view = View(timeout=None)
        play = DougButton(callback=self._play_button, style=ButtonStyle.primary, label='Play')
        pause = DougButton(callback=None, style=ButtonStyle.primary, label='Pause')
        stop = DougButton(callback=None, style=ButtonStyle.danger, label='Stop')
        next = DougButton(callback=None, style=ButtonStyle.primary, label='Next')
        view.add_item(play)
        view.add_item(pause)
        view.add_item(stop)
        view.add_item(next)
        return view

    @staticmethod
    async def _play_button(interaction: Interaction):
        print('play pressed')
        print(interaction)

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
