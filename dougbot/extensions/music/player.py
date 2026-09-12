import asyncio
import hashlib
import os
from asyncio import CancelledError
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import discord
from discord import Message, Embed
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.voice import VoiceClient
from youtube_search import YoutubeSearch

from dougbot.common import voiceutils
from dougbot.common.logger import Logger
from dougbot.config import EXTENSION_RESOURCES_DIR
from dougbot.core.bot import DougBot
from dougbot.extensions.common import webutils
from dougbot.extensions.common.annotation.miccheck import voice_command
from dougbot.extensions.common.audio.ytdl import Ytdl
from dougbot.extensions.common.file import fileutils
from dougbot.extensions.music.track import Track

_FFMPEG_OPTIONS = '-loglevel quiet'


class SoundPlayer(commands.Cog):
    CLIP_DIR = os.path.join(EXTENSION_RESOURCES_DIR, 'music', 'audio')
    CACHE_DIR = os.path.join(EXTENSION_RESOURCES_DIR, 'music', 'cache')
    THREAD_POOL = ThreadPoolExecutor()

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.loop = self.bot.loop
        self.bot.event(self.on_voice_state_update)

        self._play_queue = asyncio.Queue()
        self._entry_lock = asyncio.Lock()
        self._active_voice: VoiceClient | None = None
        self._player_loop_task: asyncio.Task | None = None
        self._prepare_track_tasks: set[asyncio.Task] = set()
        self._path_cache = {}
        self._generation = 0

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def play(self, ctx: Context, source: str):
        generation = self._generation

        track = Track(source, generation, ctx)

        async with self._entry_lock:
            if generation != self._generation:
                # Kill off any plays that occurred during stop command processing
                return

            if self._player_loop_task is None or self._player_loop_task.done():
                self._player_loop_task = asyncio.create_task(self._player_loop())

            await self._play_queue.put(track)

        task = asyncio.create_task(self._prepare_track(track))
        self._prepare_track_tasks.add(task)
        task.add_done_callback(self._prepare_track_tasks.discard)

    # Searches for a YouTube video based on the search terms given and sends the url to the play function
    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def ytplay(self, ctx, *, search_terms: str):
        yt_url = ''

        if await webutils.is_link(search_terms):
            yt_url = search_terms
        else:
            results = YoutubeSearch(search_terms, max_results=20).to_dict()
            for i in range(0, len(results)):
                if results[i]['publish_time'] != 0:
                    yt_url = f"https://www.youtube.com{results[i]['url_suffix']}"
                    break

        if yt_url:
            await self.play(ctx, source=yt_url, times='1')
            await ctx.send(f'Added {yt_url} to the queue')
        else:
            await ctx.send('Could not find track to add')

    @commands.command(aliases=['leave2'])
    @commands.guild_only()
    @voice_command()
    async def stop(self, _):
        async with self._entry_lock:
            self._generation += 1

            if self._player_loop_task:
                self._player_loop_task.cancel()

                try:
                    await self._player_loop_task
                except asyncio.CancelledError:
                    pass

                self._player_loop_task = None

            if self._active_voice:
                if self._active_voice.is_connected():
                    await self._active_voice.disconnect(force=True)

                self._active_voice = None

            while not self._play_queue.empty():
                try:
                    self._play_queue.get_nowait()
                    self._play_queue.task_done()
                except asyncio.QueueEmpty:
                    break

            for task in list(self._prepare_track_tasks):
                task.cancel()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def pause(self, ctx: Context):
        voice = await self._get_voice(ctx, allow_join=False)
        if voice is not None and voice.is_playing():
            voice.pause()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def resume(self, ctx: Context):
        voice = await self._get_voice(ctx, allow_join=False)
        if voice is not None and voice.is_paused():
            voice.resume()

    @commands.command()
    @commands.guild_only()
    @voice_command()
    async def skip(self, ctx: Context):
        voice = await self._get_voice(ctx, allow_join=False)
        if voice is not None and voice.is_playing():
            voice.stop()

    @tasks.loop(minutes=60)
    async def clear_path_cache(self):
        self._path_cache.clear()

    async def on_voice_state_update(self, member, _, __):
        # Avoid warnings when passing to stop
        none_context: Context | None = None

        # Bot was disconnected
        if member.id == self.bot.user.id:
            if member.voice is None:
                await self.stop(none_context)
            return

        # Allow for accidental human leaves
        await asyncio.sleep(5)

        if self._active_voice is None or self._active_voice.channel is None:
            return

        channel_id = self._active_voice.channel.id
        channel = member.guild.get_channel(channel_id)

        if channel is None:
            return

        humans = [m for m in channel.members if not m.bot]

        if len(humans) == 0:
            await self.stop(none_context)

    async def _player_loop(self):
        while True:
            track = await self._play_queue.get()

            try:
                await track.ready.wait()

                if track.exception:
                    raise track.exception

                if track.generation != self._generation:
                    return

                self._active_voice = await self._get_voice(track.ctx)

                finished = self.loop.create_future()

                source = discord.FFmpegPCMAudio(track.source_path, options=_FFMPEG_OPTIONS)

                if track.progress_message is not None and track.video_info is not None:
                    await track.progress_message.edit(embed=self._status_embed(track.video_info, playing=True))

                self._active_voice.play(source, after=partial(self._play_finished, finished))

                await finished
            except CancelledError:
                raise
            except Exception as e:
                Logger(__file__) \
                    .message('Failed to play audio track') \
                    .add_field('source', track.source) \
                    .exception(e) \
                    .error()
            finally:
                self._play_queue.task_done()

    def _play_finished(self, finished: asyncio.Future, error):
        # NOTE: This method gets called from a synchronous thread
        def complete(finished_future, err):
            if finished_future.done():
                return

            if error:
                finished_future.set_exception(err)
            else:
                finished_future.set_result(None)

        self.loop.call_soon_threadsafe(complete, finished, error)

    async def _prepare_track(self, track: Track):
        if track.generation != self._generation:
            return

        try:
            is_link = await webutils.is_link(track.source)

            if is_link:
                await self._download_link(track)
            elif track.source in self._path_cache:
                track.source_path = self._path_cache[track.source]
            else:
                track.source_path = await fileutils.find_file_async(self.CLIP_DIR, track.source)
                if track.source_path:
                    self._path_cache[track.source] = track.source_path
                else:
                    raise FileNotFoundError(f'Failed to find track source: {track.source}')
        except Exception as e:
            track.exception = e
        finally:
            track.ready.set()

    async def _download_link(self, track: Track):
        link = track.source

        file_path = os.path.join(self.CACHE_DIR, await self._link_hash(link))
        if os.path.exists(file_path):
            track.source_path = file_path
            return

        video_info = await self.bot.loop.run_in_executor(self.THREAD_POOL, Ytdl.info, link)
        if video_info is None or not all(key in video_info for key in ('duration', 'thumbnails', 'title', 'uploader')):
            Logger(__file__) \
                .message('Track info missing expected keys') \
                .add_field('info', video_info) \
                .error()

            video_info = {} if video_info is None else video_info

        status_embed_message = await track.ctx.send(embed=self._status_embed(video_info))

        track.source_path = file_path
        track.video_info = video_info
        track.progress_message = status_embed_message

        progress_hook = partial(self._progress_hook, video_info, status_embed_message)

        await self.bot.loop.run_in_executor(self.THREAD_POOL, Ytdl.download, link, file_path, progress_hook)

    def _progress_hook(self, video_info: dict, message: Message, data):
        # NOTE: This method is called from a synchronous thread
        if message is None or data is None:
            Logger(__file__) \
                .message('Progress hook null argument') \
                .add_field('msg', message) \
                .add_field('data', data) \
                .error()

            return

        asyncio.run_coroutine_threadsafe(message.edit(embed=self._status_embed(video_info, data)), self.bot.loop)

    @classmethod
    def _status_embed(cls, video_info: dict, fields: dict = None, playing: bool = False):
        progress_display = cls._progress_display(fields)

        if progress_display.get('Progress') == 'Error':
            embed_title = 'Failed'
        elif playing:
            embed_title = 'Playing'
        else:
            embed_title = 'Downloading'

        uploader = video_info.get('uploader', 'Unknown')
        video_title = video_info.get('title', 'Unknown')
        url = video_info.get('webpage_url', 'Unknown')

        thumbnails = video_info.get('thumbnails') or []
        thumbnail = thumbnails[-1].get('url') if thumbnails else None

        description_markdown = f'Uploader: {uploader}\n\n[{video_title}]({url})'

        embed = Embed(title=embed_title, description=description_markdown, color=0xFF0000).set_image(url=thumbnail)

        for name, value in progress_display.items():
            embed.add_field(name=name, value=value)

        duration = video_info.get('duration', '00:00:00')

        if duration is not None and playing:
            duration = int(duration)
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours:
                duration_string = f'{hours}:{minutes:02}:{seconds:02}'
            else:
                duration_string = f'{minutes}:{seconds:02}'

            embed.add_field(name='Duration', value=duration_string)

        return embed

    async def _get_voice(self, ctx: Context, allow_join=True):
        if self._active_voice is None and allow_join:
            voice = await voiceutils.join_voice_channel(ctx.message.author.voice.channel, self.bot)
        elif self._active_voice.channel == ctx.message.author.voice.channel:
            voice = self._active_voice
        else:
            raise ValueError(f'{ctx.message.author} not in same voice channel')

        if not voice:
            raise ValueError('Failed to get voice')

        return voice

    @staticmethod
    def _progress_display(data: dict):
        if data is None or 'status' not in data:
            return {'Progress': 'Starting...'}

        if data['status'] == 'error':
            return {'Progress': 'Error'}
        elif data['status'] == 'finished':
            return {'Progress': '100%'}

        result = {}

        total_size = data.get('total_bytes') or data.get('total_bytes_estimate')
        downloaded = data.get('downloaded_bytes', 0)

        if total_size is not None:
            result['Progress'] = f"{int(downloaded / total_size * 100)}%"
        else:
            result['Progress'] = "Can't be determined"

        eta = data.get('eta')

        if eta is None:
            speed = data.get('speed')

            if total_size is not None and speed:
                eta = (total_size - downloaded) / speed

        if eta is not None:
            eta = int(eta)
            minutes, seconds = divmod(eta, 60)

            if minutes:
                result['ETA'] = f"{minutes}m {seconds}s"
            else:
                result['ETA'] = f"{seconds}s"

        return result

    @staticmethod
    async def _link_hash(link):
        md5hash = hashlib.new('md5')
        md5hash.update(f'sp_{link}'.encode('utf-8'))
        return md5hash.hexdigest()


def setup(bot):
    bot.add_cog(SoundPlayer(bot))
