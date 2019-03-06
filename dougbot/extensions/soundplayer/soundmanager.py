import os
import shutil

import requests
from discord.ext import commands


class SoundManager:
    _CLIPS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'res', 'audio')

    SUPPORTED_FILE_TYPES = ['.mp3', '.m4a']

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def renameclip(self, ctx, from_clip: str, *, to_clip: str):
        # TODO
        """if not await self._is_admin(ctx.message.author.roles):
            await self.bot.confusion(ctx.message, "Command 'deleteclip' is only for users with Admin role.")
            return

        if '..' in from_clip or os.path.isabs(from_clip) or '..' in to_clip or os.path.isabs(to_clip):
            await self.bot.confusion(ctx.message)
            return

        from_path = await self._get_clip_path(from_clip)

        if from_path is None:
            await self.bot.confusion(ctx.message)
            return

        to_path =

        try:
            os.rename(from_path, to_path)
        except OSError:
            await self.bot.confusion(ctx.message)
            return"""
        pass

    @commands.command(pass_context=True, no_pm=True)
    async def deleteclip(self, ctx, *, clip: str):
        if not await self._is_admin(ctx.message.author.roles):
            await self.bot.confusion(ctx.message, "Command 'deleteclip' is only for users with Admin role.")
            return

        if '..' in clip or os.path.isabs(clip):
            await self.bot.confusion(ctx.message)
            return

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
        if '..' in clip or os.path.isabs(clip):
            await self.bot.confusion(ctx.message)
            return

        path = await self._get_clip_path(clip)

        if path is None:
            await self.bot.confusion(ctx.message)
            return

        await self.bot.upload(path)

    @commands.command(pass_context=True)
    async def addclip(self, ctx, dest: str, filename: str, *, url: str = None):
        if '..' in dest or os.path.isabs(dest):
            await self.bot.confusion(ctx.message)
            return

        if not os.path.exists(os.path.join(self._CLIPS_DIR, dest)):
            os.makedirs(os.path.join(self._CLIPS_DIR, dest), exist_ok=True)

        if url is not None and not await self._check_url(url):
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
        except Exception:
            await self.bot.confusion(ctx.message)
            return

        await self.bot.confirmation(ctx.message)

    @commands.command(aliases=['list'])
    async def clips(self, *, category: str = None):
        to_print = []
        if category in ['cats', 'cat', 'category', 'categories']:
            to_print = filter(lambda f: os.path.isdir(os.path.join(self._CLIPS_DIR, f)), os.listdir(self._CLIPS_DIR))
        else:
            base = os.path.join(self._CLIPS_DIR, category) if category is not None else self._CLIPS_DIR
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
    async def _is_admin(roles):
        return roles is not None and next(filter(lambda role: role.name == 'Admin', roles), None) is not None

    async def _get_clip_path(self, clip):
        for dirpath, dirnames, filenames in os.walk(self._CLIPS_DIR):
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

    async def download_file(self, url):
        if not await self._check_url(url):
            return None
        # TODO ASYNC
        return requests.get(url, stream=True)


def setup(bot):
    bot.add_cog(SoundManager(bot))
