import os
import shutil
import sys

import requests
from discord.ext import commands

from dougbot.extensions.util.admin_check import admin_command


class SoundManager:
    CLIPS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'res', 'audio')
    SUPPORTED_FILE_TYPES = ['.mp1', '.mp2', '.mp3', '.mp4', '.m4a', '.3gp', '.aac', '.flac', '.wav', '.aif']

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    @admin_command()
    async def renameclip(self, ctx, from_clip: str, *, to_clip: str):
        clip_path = await self._get_clip_path(from_clip)
        if clip_path is None:
            await self.bot.confusion(ctx.message)
            return

        clip_basename = os.path.basename(clip_path)
        dest_path = clip_path[:-len(clip_basename)]
        dest_path = os.path.join(dest_path, f"{to_clip}{clip_basename[clip_basename.rfind('.'):]}")

        try:
            os.rename(clip_path, dest_path)
        except OSError:
            await self.bot.confusion(ctx.message)
            return

    @commands.command(pass_context=True)
    @admin_command()
    async def moveclip(self, ctx, clip: str, *, dest: str):
        clip_path = await self._get_clip_path(clip)
        if clip_path is None:
            await self.bot.confusion(ctx.message)
            return

        dest_path = os.path.join(self.CLIPS_DIR, dest)
        if not os.path.exists(dest_path):
            try:
                os.makedirs(dest_path, exist_ok=True)
            except OSError:
                await self.bot.confusion(ctx.message)
                return

        try:
            dest_path = os.path.join(dest_path, os.path.basename(clip_path))
            os.rename(clip_path, dest_path)
        except OSError:
            await self.bot.confusion(ctx.message)
            return

    @commands.command(pass_context=True, no_pm=True)
    @admin_command()
    async def deleteclip(self, ctx, *, clip: str):
        path = await self._get_clip_path(clip)
        if path is None:
            await self.bot.confusion(ctx.message)
            return

        try:
            os.remove(path)
        except OSError:
            await self.bot.confusion(ctx.message)
            return

        await self.bot.confirmation(ctx.message)

    @commands.command(pass_context=True)
    async def getclip(self, ctx, *, clip: str):
        path = await self._get_clip_path(clip)

        if path is None:
            await self.bot.confusion(ctx.message)
            return

        await self.bot.upload(path)

    @commands.command(pass_context=True)
    async def addclip(self, ctx, dest: str, filename: str, *, url: str = None):
        if not await self._safe_path(dest):
            await self.bot.confusion(ctx.message)
            return

        if not os.path.exists(os.path.join(self.CLIPS_DIR, dest)):
            try:
                os.makedirs(os.path.join(self.CLIPS_DIR, dest), exist_ok=True)
            except Exception as e:
                await self.bot.confusion(ctx.message)
                return

        if url is None:
            # If no url was provided, then there has to be an audio attachment.
            if len(ctx.message.attachments) <= 0:
                await self.bot.confusion(ctx.message)
                return
            url = ctx.message.attachments[0]['url']

        if not await self._check_url(url):
            await self.bot.confusion(ctx.message)
            return

        if '.' in filename and filename[filename.rfind('.'):] not in self.SUPPORTED_FILE_TYPES:
            await self.bot.confusion(ctx.message, f"{filename[filename.rfind('.'):]} unsupported file type.")
            return
        elif '.' not in filename:
            filename += url[url.rfind('.'):]

        file = await self._download_file(url)
        if file is None:
            await self.bot.confusion(ctx.message)
            return

        path = os.path.join(self.CLIPS_DIR, f'{dest}', filename.lower())
        try:
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(file.raw, out_file)
        except Exception as e:
            print(f'ERROR: Failed to write sound file: {e}', file=sys.stderr)
            await self.bot.confusion(ctx.message)
            return

        await self.bot.confirmation(ctx.message)

    @commands.command(aliases=['list'])
    async def clips(self, *, category: str = None):
        to_print = []
        if category in ['cats', 'cat', 'category', 'categories']:
            to_print = filter(lambda f: os.path.isdir(os.path.join(self.CLIPS_DIR, f)), os.listdir(self.CLIPS_DIR))
        else:
            base = os.path.join(self.CLIPS_DIR, category) if category is not None else self.CLIPS_DIR
            for dirpath, dirnames, filenames in os.walk(base):
                for file in filenames:
                    if await self._is_audio_track(file):
                        to_print.append(file[:file.rfind('.')])

        to_print = sorted(to_print, key=lambda s: s.casefold())
        enter = ''
        message = ''

        for p in to_print:
            message += enter + p
            enter = '\n'

        if len(message) > 0:
            await self.bot.say(message)

    @staticmethod
    async def _safe_path(path):
        return path is not None and '..' not in path and not os.path.isabs(path)

    async def _get_clip_path(self, clip):
        for dirpath, dirnames, filenames in os.walk(self.CLIPS_DIR):
            for file in filenames:
                if '.' in file and file[:file.rfind('.')] == clip:
                    return os.path.join(dirpath, file)
        return None

    async def _is_audio_track(self, file):
        return type(file) == str and '.' in file and file[file.rfind('.'):] in self.SUPPORTED_FILE_TYPES

    @staticmethod
    async def _is_link(candidate):
        if type(candidate) != str:
            return False
        # Rudimentary link detection
        return candidate.startswith('https://') or candidate.startswith('http://') or candidate.startswith('www.')

    async def _check_url(self, url):
        return url is not None and await self._is_link(url) and '.' in url \
               and url[url.rfind('.'):] in self.SUPPORTED_FILE_TYPES

    async def _download_file(self, url):
        if not await self._check_url(url):
            return None
        # TODO ASYNC
        return requests.get(url, stream=True)


def setup(bot):
    bot.add_cog(SoundManager(bot))
