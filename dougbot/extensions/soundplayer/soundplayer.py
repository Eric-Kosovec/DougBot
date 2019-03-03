import asyncio
import os
import shutil

import requests
from discord.ext import commands

from dougbot.extensions.soundplayer.track import Track
from dougbot.extensions.error.error import TrackNotExistError
from dougbot.util.cache import LRUCache
from dougbot.util.queue import Queue


class SoundPlayer:
    _CLIPS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _CLIPS_DIR = os.path.join(_CLIPS_DIR, 'res', 'audio')

    SUPPORTED_FILE_TYPES = ['.mp3', '.m4a']

    def __init__(self, bot):
        self.bot = bot
        self._path_cache = LRUCache(15)
        self._play_lock = asyncio.Lock()
        self._sound_queue = Queue()
        self._volume = 1.0
        self._player = None
        self._voice = None

    '''
    Context (CTX) variables: 'args', 'bot', 'cog',
    'command', 'invoke', 'invoked_subcommand',
    'invoked_with', 'kwargs', 'message', 'prefix',
    'subcommand_passed', 'view'
    '''
    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        # Commander is not in a voice channel, or bot is already in a voice channel on the server
        if ctx.message.author.voice is None or self.bot.voice_client_in(ctx.message.server) is not None:
            return
        self._voice = await self.bot.join_channel(ctx.message.author.voice.voice_channel)

    # Aliases are additional command names beyond the method name.
    @commands.command(aliases=['stop'], pass_context=True, no_pm=True)
    async def leave(self, ctx):
        if ctx.message.author.voice is None:
            return

        bot_voice_client = self.bot.voice_client_in(ctx.message.server)

        # Bot not in a voice channel or user is not in the same voice channel
        if bot_voice_client is None or bot_voice_client.channel != ctx.message.author.voice.voice_channel:
            return

        await self._quit_playing()
        await self.bot.leave_channel(bot_voice_client.channel)

    # Synchronized code
    @commands.command(aliases=['sb'], pass_context=True, no_pm=True)
    async def play(self, ctx, *, audio: str):
        # The '*' denotes consume rest, which will take all text after command name to be the argument

        if self._voice is None:
            # Note: you cannot just call a different command's method, so you need a create common method, if necessary.
            self._voice = await self.bot.join_channel(ctx.message.author.voice.voice_channel)

        try:
            await self._sound_queue.put(await self._create_track(audio))
        except TrackNotExistError:
            await self.bot.confusion(ctx.message)
            return

        # Acquire lock so only one thread will play at once; otherwise, sounds will interleave.
        await self._play_lock.acquire()

        # Start of the Critical Section
        try:
            await self._play_top_track()
        except Exception as e:
            self._play_lock.release()
            raise e

    def _soundplayer_finished(self):
        try:
            asyncio.run_coroutine_threadsafe(self._unlock_play_lock(), self.bot.loop).result()
        except Exception as e:
            raise e

    async def _unlock_play_lock(self):
        self._play_lock.release()
        # End of the Critical Section

    @commands.command(aliases=['volume'], no_pm=True)
    async def vol(self, volume: float):
        self._volume = max(0.0, min(100.0, volume)) / 100.0
        if self._player is not None:
            self._player.volume = self._volume

    @commands.command(no_pm=True)
    async def pause(self):
        if self._player is not None:
            self._player.pause()

    @commands.command(no_pm=True)
    async def resume(self):
        if self._player is not None:
            self._player.resume()

    @commands.command(no_pm=True)
    async def skip(self):
        # Cause the player to stop and call the registered callback, which will start the next track.
        if self._player is not None:
            self._player.stop()

    @commands.command(pass_context=True, no_pm=True)
    async def addclip(self, ctx, dest: str, filename: str, *, url: str=None):
        if '..' in dest or os.path.isabs(dest):
            await self.bot.confusion(ctx.message)
            return

        if not os.path.exists(os.path.join(self._CLIPS_DIR, dest)):
            os.makedirs(os.path.join(self._CLIPS_DIR, dest), exist_ok=True)

        # TODO PUT A LIMIT ON SIZE OF SOUND CLIP FOLDER

        if url is not None and not await self.check_url(url):
            await self.bot.confusion(ctx.message)
            return

        if url is None:
            # If no url was provided, then there has to be an audio attachment.
            if len(ctx.message.attachments) <= 0:
                await self.bot.confusion(ctx.message)
                return
            url = ctx.message.attachments[0]['url']

        if '.' in filename and not filename[filename.rfind('.'):] in self.SUPPORTED_FILE_TYPES:
            await self.bot.confusion(ctx.message)
            return
        elif '.' not in filename:
            filename += url[url.rfind('.'):]

        file = await self.download_file(url)

        if file is None:
            await self.bot.confusion(ctx.message)
            return

        path = os.path.join(self._CLIPS_DIR, f'{dest}')

        if not os.path.exists(path):
            await self.bot.confusion(ctx.message)
            return

        path = os.path.join(path, filename.lower())

        try:
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(file.raw, out_file)
        except Exception as e:
            await self.bot.confusion(ctx.message)
            return

        # TODO PUSH TO GITHUB

        await self.bot.confirmation(ctx.message)

    async def check_url(self, url):
        if url is None:
            return False
        if not await self._is_link(url):
            return False
        if '.' in url and url[url.rfind('.'):] not in self.SUPPORTED_FILE_TYPES:
            return False
        return True

    async def download_file(self, url):
        if not await self.check_url(url):
            return None
        # TODO ASYNC
        return requests.get(url, stream=True)

    @commands.command(aliases=['list'])
    async def clips(self, category: str=None):
        if category in ['cats', 'cat', 'category', 'categories']:
            enter = ''
            clip_message = 'Categories:\n'
            base_folders = [self._CLIPS_DIR] + list(filter(lambda f: os.path.isdir(os.path.join(self._CLIPS_DIR, f)),
                                                           os.listdir(self._CLIPS_DIR)))
            for folder in base_folders[1:]:
                clip_message += enter + folder
                enter = '\n'

            await self.bot.say(clip_message)
            return

        base = os.path.join(self._CLIPS_DIR, category) if category is not None else self._CLIPS_DIR
        clips = []
        for dirpath, dirnames, filenames in os.walk(base):
            for file in filenames:
                if await self._is_audio_track(file):
                    clips.append(file[:file.rfind('.')])

        clips = sorted(clips, key=lambda s: s.casefold())
        enter = ''
        clip_message = ''

        for clip in clips:
            clip_message += enter + clip
            enter = '\n'

        await self.bot.say(clip_message)

    # Listening for events will be registered just by making a method with prefix 'on_voice.'
    async def on_voice_state_update(self, before, after):
        if before is None or after is None or self._voice is None:
            return

        if before.voice_channel is None or before.voice_channel == after.voice_channel:
            return

        if before.voice_channel == self._voice.channel and await self._are_human_members(self._voice.channel):
            await self._quit_playing()
            await self.bot.leave_channel(before.voice_channel)

    @staticmethod
    async def _are_human_members(channel):
        human_count = 0
        if channel is None:
            return False
        for member in channel.voice_members:
            if not member.bot:
                human_count += 1
        return human_count >= 1

    async def _quit_playing(self):
        await self._sound_queue.clear()

        if self._player is not None:
            self._player.stop()
            self._player = None

        if self._voice is not None:
            await self._voice.disconnect()
            self._voice = None

    async def _play_top_track(self):
        if await self._sound_queue.empty():
            return

        self._player = await self._get_player(self._voice, await self._sound_queue.get())
        self._player.volume = self._volume
        self._player.start()

    async def _is_audio_track(self, candidate):
        if type(candidate) != str:
            return False

        for ending in self.SUPPORTED_FILE_TYPES:
            if candidate.endswith(ending):
                return True

        return False

    @staticmethod
    async def _is_link(candidate):
        if type(candidate) != str:
            return False
        # Rudimentary link detection
        return candidate.startswith('https://') or candidate.startswith('http://') or candidate.startswith('www.')

    async def _get_player(self, vc, track):
        if vc is None or track is None:
            return None
        callback = self._soundplayer_finished
        if not track.is_link:
            player = vc.create_ffmpeg_player(track.src, after=callback)
        else:
            player = await vc.create_ytdl_player(track.src, after=callback)
        return player

    async def _create_track(self, src):
        is_link = await self._is_link(src)
        if not is_link:
            src = await self._create_path(src, self._CLIPS_DIR, self._path_cache)
        return Track(src, is_link)

    async def _create_path(self, audio, clip_base, path_cache):
        if audio is None or clip_base is None or path_cache is None:
            return None

        audio_path = await path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        for dirpath, dirnames, filenames in os.walk(clip_base):
            for ending in self.SUPPORTED_FILE_TYPES:
                if f'{audio}{ending}'.lower() in self._lowercase_gen(filenames):
                    audio_path = os.path.join(dirpath, f'{audio}{ending}')
                    await path_cache.insert(audio, audio_path)
                    return audio_path

        return None

    @staticmethod
    def _lowercase_gen(strings):
        for string in strings:
            yield string.lower()


def setup(bot):
    bot.add_cog(SoundPlayer(bot))
