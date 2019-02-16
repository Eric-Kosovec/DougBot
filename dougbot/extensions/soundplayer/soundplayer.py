import asyncio
import os
import shutil
import subprocess

import requests
from discord.ext import commands

from dougbot.extensions.soundplayer.track import Track
from dougbot.util.cache import LRUCache
from dougbot.util.queue import Queue


class SoundPlayer:
    _CLIPS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _CLIPS_DIR = os.path.join(_CLIPS_DIR, 'res', 'audio')

    SUPPORTED_FILE_TYPES = ['.mp3', '.m4a']

    def __init__(self, bot):
        self.bot = bot
        self.path_cache = LRUCache(15)
        self.play_lock = asyncio.Lock()
        self.sound_queue = Queue()
        self.volume = 1.0
        self.player = None
        self.voice = None

    # Context variables: 'args', 'bot', 'cog',
    # 'command', 'invoke', 'invoked_subcommand',
    # 'invoked_with', 'kwargs', 'message', 'prefix',
    # 'subcommand_passed', 'view'
    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        # Commander is not in a voice channel, or bot is already in a voice channel on the server
        if ctx.message.author.voice is None or self.bot.voice_client_in(ctx.message.server) is not None:
            return

        self.voice = await self.bot.join_channel(ctx.message.author.voice.voice_channel)

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

    # Aliases are additional command names beyond the method name.
    @commands.command(aliases=['sb'], pass_context=True, no_pm=True)
    async def play(self, ctx, *, audio: str):
        # The '*' denotes consume rest, which will take all text after command name to be the argument

        if self.voice is None:
            self.voice = await self.bot.join_channel(ctx.message.author.voice.voice_channel)

        # TODO PUT THE SAME TRACK INTO ONE, SO THERE IS NO NEED FOR EXTRA COMPUTATION
        await self.sound_queue.put(await self._create_track(audio))

        # Acquire lock so only one thread will play at once; otherwise, sounds will interleave.
        await self.play_lock.acquire()

        # Start of the Critical Section
        try:
            await self._play_top_track()
        except Exception as e:
            self.play_lock.release()
            raise e

    @commands.command(aliases=['volume'], no_pm=True)
    async def vol(self, volume: float):
        self.volume = max(0.0, min(100.0, volume)) / 100.0
        if self.player is not None:
            self.player.volume = self.volume

    @commands.command(no_pm=True)
    async def pause(self):
        if self.player is not None:
            self.player.pause()

    @commands.command(no_pm=True)
    async def resume(self):
        if self.player is not None:
            self.player.resume()

    @commands.command(no_pm=True)
    async def skip(self):
        # Cause the player to stop and call the registered callback, which will start the next track.
        if self.player is not None:
            self.player.stop()

    @commands.command(pass_context=True, no_pm=True)
    async def addclip(self, ctx, dest: str, filename: str, *, url: str=None):
        # TODO For now, disallow going into subfolders until cliplisting and finding can do the same.
        if '..' in dest or '/' in dest:
            await self.bot.confusion(ctx.message)
            return

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

        await self.bot.confirmation(ctx.message)

    async def check_url(self, url):
        if url is None:
            return False
        if not (url.startswith('http://') or url.startswith('https://')):
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
        clips = []

        base_folders = [self._CLIPS_DIR] + list(filter(lambda f: os.path.isdir(os.path.join(self._CLIPS_DIR, f)),
                                                       os.listdir(self._CLIPS_DIR)))

        if category in ['cat', 'category', 'categories']:
            enter = ''
            clip_message = 'Categories:\n'
            for folder in base_folders[1:]:
                clip_message += enter + folder
                enter = '\n'

            await self.bot.say(clip_message)
            return

        # TODO RECURSIVE FOR SUBFOLDERS

        for folder in base_folders:
            if category is not None and folder != category:
                continue
            if folder == self._CLIPS_DIR:
                search_space = [self._CLIPS_DIR]
            else:
                search_space = os.listdir(os.path.join(self._CLIPS_DIR, folder))

            for file in search_space:
                if await self._is_audio_track(file):
                    clips.append(file[:file.rfind('.')])

        enter = ''
        clip_message = ''

        clips = sorted(clips, key=lambda s: s.casefold())

        for clip in clips:
            clip_message += enter + clip
            enter = '\n'

        await self.bot.say(clip_message)

    @commands.command(pass_context=True)
    async def refresh(self, ctx):
        cwd = os.getcwd()
        os.chdir('../..')
        try:
            subprocess.check_call(['git', 'checkout', 'master', 'dougbot/res/audio'])
            subprocess.check_call(['git', 'checkout', 'master', 'dougbot/res/image'])
        except subprocess.CalledProcessError:
            await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)

    async def on_voice_state_update(self, before, after):
        if before is None or after is None or self.voice is None:
            return

        if before.voice_channel is None or before.voice_channel == after.voice_channel:
            return

        if before.voice_channel == self.voice.channel and len(self.voice.channel.voice_members) <= 1:
            await self._quit_playing()
            await self.bot.leave_channel(before.voice_channel)

    async def _quit_playing(self):
        await self.sound_queue.clear()

        if self.player is not None:
            self.player.stop()
            self.player = None

        if self.voice is not None:
            await self.voice.disconnect()
            self.voice = None

    async def _play_top_track(self):
        if await self.sound_queue.empty():
            return

        self.player = await self._get_player(self.voice, await self.sound_queue.get())
        self.player.volume = self.volume
        self.player.start()

    async def _unlock_play_lock(self):
        self.play_lock.release()
        # End of the Critical Section

    def _soundplayer_finished(self):
        try:
            asyncio.run_coroutine_threadsafe(self._unlock_play_lock(), self.bot.loop).result()
        except Exception as e:
            raise e

    async def _is_audio_track(self, candidate):
        if type(candidate) != str:
            return False
        for ending in self.SUPPORTED_FILE_TYPES:
            if candidate.endswith(ending):
                return True
        return False

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
        is_link = False

        # Rudimentary link detection
        if src.startswith('https://') or src.startswith('http://') or src.startswith('www.'):
            is_link = True
        else:
            src = await self._create_path(src, self._CLIPS_DIR, self.path_cache)

        return Track(src, is_link)

    # TODO MAYBE LOAD ALL CLIPS INTO DICT UPON CREATION INSTEAD
    async def _create_path(self, audio, clip_base, path_cache):
        if audio is None or clip_base is None or path_cache is None:
            return None

        audio_path = await path_cache.get(audio)
        if audio_path is not None:
            return audio_path

        # Search for clip in the base directory, but not in a folder
        for ending in self.SUPPORTED_FILE_TYPES:
            if f'{audio}{ending}'.lower() in self._lower_case_dir_listing(clip_base):
                audio_path = os.path.join(clip_base, f'{audio}{ending}')
                await path_cache.insert(audio, audio_path)
                return audio_path

        # Find clip within folder
        for file in os.listdir(clip_base):
            if os.path.isdir(os.path.join(clip_base, file)):
                for ending in self.SUPPORTED_FILE_TYPES:
                    if f'{audio}{ending}'.lower() in self._lower_case_dir_listing(os.path.join(clip_base, file)):
                        audio_path = os.path.join(clip_base, file, f'{audio}{ending}')
                        break
            if audio_path is not None:
                break

        if audio_path is not None:
            await path_cache.insert(audio, audio_path)

        return audio_path

    @staticmethod
    def _lower_case_dir_listing(path):
        for item in os.listdir(path):
            yield item.lower()


def setup(bot):
    bot.add_cog(SoundPlayer(bot))
