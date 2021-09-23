import asyncio
import functools
import hashlib
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor

import discord
import youtube_dl
from discord.ext import commands

from dougbot.common.cache import LRUCache
from dougbot.core.bot import DougBot
from dougbot.extensions.common.autocorrect import Autocorrect
from dougbot.extensions.common.annotations.miccheck import voice_command
from dougbot.extensions.music.error import TrackNotExistError
from dougbot.extensions.music.supportedformats import PLAYER_FILE_TYPES
from dougbot.extensions.music.track import Track


class SoundPlayer2(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        #self.bot.event(self.on_voice_state_update)

        self._path_cache = LRUCache(20)
        self._thread_pool = ThreadPoolExecutor()

        self._clips_dir = os.path.join(self.bot.ROOT_DIR, 'resources', 'extensions', 'music', 'audio')
        self._cache_dir = os.path.join(self.bot.ROOT_DIR, 'cache')
        #self._autocorrect = Autocorrect(self._clip_names())  # Hack until rewrite
        self._kv = self.bot.kv_store()
        self._play_lock = asyncio.Lock()  # Stop multiple threads from being created and playing audio over each other.
        self._notify_done_playing = asyncio.Semaphore(0)  # For notifying thread is done playing clip
        self._links_to_play = 0
        self._volume = 1.0 if not self._kv.contains('volume') else self._kv['volume']
        self._skip = False

        # Producer
        @commands.command()
        @commands.guild_only()
        @voice_command()
        async def play2(self, ctx, source: str, *, times: str = '1'):
            source, times = await self._custom_play_parse(source, times)
            if times <= 0:
                await self.bot.confusion(ctx.message)
                return

            if self._channel is None:
                self._channel = ctx.message.author.voice.channel
            elif self._channel.id != ctx.message.author.voice.channel.id:  # Don't join a voice channel if bot is already in one.
                return

            # Keep ordering of clips
            async with self._order_lock:
                task = functools.partial(self._insert_audio, source, times)
                await self.bot.loop.run_in_executor(self._thread_pool, task)
