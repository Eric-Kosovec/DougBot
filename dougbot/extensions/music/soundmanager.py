import os
import shutil
import sys

import discord
import requests
from discord.ext import commands

from dougbot.extensions.music.supportedformats import PLAYER_FILE_TYPES
from dougbot.extensions.util.admin_check import admin_command


class SoundManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._clips_dir = os.path.join(self.bot.ROOT_DIR, 'resources', 'audio')

    @commands.command()
    @admin_command()
    async def renameclip(self, ctx, from_clip: str, *, to_clip: str):
        clip_path = await self._get_clip_path(from_clip)
        if clip_path is None:
            await self.bot.confusion(ctx.message)
            return

        clip_basename = os.path.basename(clip_path)
        dest_path = os.path.join(os.path.dirname(clip_path), f'{to_clip}{clip_basename[clip_basename.rfind("."):]}')
        try:
            os.rename(clip_path, dest_path)
        except OSError:
            await self.bot.confusion(ctx.message)
            return

        await self.bot.confirmation(ctx.message)

    @commands.command()
    @admin_command()
    async def moveclip(self, ctx, clip: str, *, dest: str):
        clip_path = await self._get_clip_path(clip)
        if clip_path is None:
            await self.bot.confusion(ctx.message)
            return

        dest_path = os.path.join(self._clips_dir, dest)
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

        await self.bot.confirmation(ctx.message)

    @commands.command(aliases=['removeclip'])
    @admin_command()
    async def deleteclip(self, ctx, *, clip: str):
        clip_path = await self._get_clip_path(clip)
        if clip_path is None:
            await self.bot.confusion(ctx.message)
            return

        try:
            os.remove(clip_path)
        except OSError:
            await self.bot.confusion(ctx.message)
            return

        await self.bot.confirmation(ctx.message)

    @commands.command()
    async def getclip(self, ctx, *, clip: str):
        path = await self._get_clip_path(clip)
        if path is None:
            await self.bot.confusion(ctx.message)
            return
        await ctx.send(file=discord.File(path))

    @commands.command()
    async def addclip(self, ctx, folder: str, clip_name: str, *, url: str = None):
        if not await self._safe_path(folder):
            await self.bot.confusion(ctx.message)
            return

        if not os.path.exists(os.path.join(self._clips_dir, folder)):
            try:
                os.makedirs(os.path.join(self._clips_dir, folder), exist_ok=True)
            except OSError:
                await self.bot.confusion(ctx.message)
                return

        if url is None or len(url) <= 0:
            # If no url was provided, then there has to be an audio attachment.
            if len(ctx.message.attachments) <= 0:
                await self.bot.confusion(ctx.message)
                return
            url = ctx.message.attachments[0].url

        if not await self._check_url(url):
            await self.bot.confusion(ctx.message)
            return

        if '.' in clip_name and clip_name[clip_name.rfind('.'):] not in PLAYER_FILE_TYPES:
            await self.bot.confusion(ctx.message, f"{clip_name[clip_name.rfind('.'):]} unsupported file type.")
            return
        elif '.' not in clip_name:
            clip_name += url[url.rfind('.'):]

        file = await self._download_file(url)
        if file is None:
            await self.bot.confusion(ctx.message)
            return

        path = os.path.join(self._clips_dir, f'{folder}', clip_name.lower())
        try:
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(file.raw, out_file)
        except Exception as e:
            print(f'ERROR: Failed to write sound file: {e}', file=sys.stderr)
            await self.bot.confusion(ctx.message)
            return

        await self.bot.confirmation(ctx.message)

    @commands.command(aliases=['list'])
    async def clips(self, ctx, *, category: str = None):
        if category is None or category == 'all':
            categories = filter(lambda f: os.path.isdir(os.path.join(self._clips_dir, f)), os.listdir(self._clips_dir))
        else:
            categories = [os.path.join(self._clips_dir, category)]
            if not os.path.isdir(categories[0]):
                await self.bot.confusion(ctx.message)
                return

        embed = discord.Embed(color=discord.Color(0xff0000))

        if category is None:  # List category names
            embed.title = '**Soundboard Categories**'
            embed.description = ' '.join([f'`{c}`' for c in categories])
        elif category == 'all':  # List all clips, sorted by category
            embed.title = '**Soundboard Clips**'
            for category in categories:
                field_value = ''

                for _, _, filenames in os.walk(os.path.join(self._clips_dir, category)):
                    field_value += ' '.join(
                        [f'`{f[:f.rfind(".")]}`' for f in filenames if await self._is_audio_track(f)]
                    )

                if len(field_value) > 0:
                    embed.add_field(name=f'**{category}**', value=field_value)
        else:  # List clips within specific category
            embed.title = f'**{category} Clips**'.title()
            description = ''
            # List clips in specific category
            for _, _, filenames in os.walk(categories[0]):
                description += ' '.join([f'`{f[:f.rfind(".")]}`' for f in filenames if await self._is_audio_track(f)])
            embed.description = description

        await ctx.send(embed=embed)

    ''' Begin private methods '''

    @staticmethod
    async def _safe_path(path):
        return path is not None and '..' not in path and not os.path.isabs(path)

    async def _get_clip_path(self, clip):
        for dirpath, _, filenames in os.walk(self._clips_dir):
            for file in filenames:
                if '.' in file and file[:file.rfind('.')] == clip:
                    return os.path.join(dirpath, file)
        return None

    @staticmethod
    async def _is_audio_track(filename):
        return type(filename) == str and '.' in filename and filename[filename.rfind('.'):] in PLAYER_FILE_TYPES

    @staticmethod
    async def _is_link(candidate):
        if type(candidate) != str:
            return False
        # Rudimentary link detection
        return candidate.startswith('https://') or candidate.startswith('http://') or candidate.startswith('www.')

    async def _check_url(self, url):
        return url is not None and await self._is_link(url) and '.' in url \
               and url[url.rfind('.'):] in PLAYER_FILE_TYPES

    async def _download_file(self, url):
        if not await self._check_url(url):
            return None
        return requests.get(url, stream=True)


def setup(bot):
    bot.add_cog(SoundManager(bot))
