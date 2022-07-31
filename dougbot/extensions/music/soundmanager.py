import os
import shutil

import nextcord
from nextcord.ext import commands

from dougbot.common.messaging import reactions
from dougbot.config import EXTENSION_RESOURCES_DIR
from dougbot.core.bot import DougBot
from dougbot.extensions.common import fileutils, webutils
from dougbot.extensions.common.annotation.admincheck import admin_command


class SoundManager(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        self._clips_dir = os.path.join(EXTENSION_RESOURCES_DIR, 'music', 'audio')

    # TODO ALLOW CLIPS TO HAVE DIRECTORIES SPECIFIED IN THEM

    @commands.command()
    @admin_command()
    async def renameclip(self, ctx, from_clip: str, *, to_clip: str):
        from_path = await fileutils.find_file_async(self._clips_dir, from_clip)
        if from_path is None:
            await reactions.confusion(ctx.message)
            return

        # TODO SPLITEXT
        if os.curdir in to_clip:
            to_clip = to_clip[:to_clip.rfind(os.curdir)]

        to_path = os.path.join(os.path.dirname(from_path), f'{to_clip}{from_path[from_path.rfind(os.curdir):]}')
        try:
            os.makedirs(to_path, exist_ok=True)
            os.rename(from_path, to_path)
            await reactions.confirmation(ctx.message)
        except OSError:
            await reactions.confusion(ctx.message)
            raise

    @commands.command()
    @admin_command()
    async def moveclip(self, ctx, clip: str, *, dest: str):
        clip_path = await fileutils.find_file_async(self._clips_dir, clip)
        if clip_path is None:
            await reactions.confusion(ctx.message)
            return

        dest_path = os.path.join(dest, os.path.basename(clip_path))
        try:
            os.makedirs(dest_path, exist_ok=True)
            os.rename(clip_path, dest_path)
            await reactions.confirmation(ctx.message)
        except OSError:
            await reactions.confusion(ctx.message)
            raise

    @commands.command(aliases=['deleteclip'])
    @admin_command()
    async def removeclip(self, ctx, *, clip: str):
        # TODO DETERMINE IF A DIRECTORY IS GIVEN IN CLIP AND SPLIT OUT
        try:
            target = await fileutils.find_file_async(self._clips_dir, clip)
            os.remove(target)
            await reactions.confirmation(ctx.message)
        except Exception:
            await reactions.confusion(ctx.message)
            raise

    @commands.command(aliases=['removecategory'])
    @admin_command()
    async def removecat(self, ctx, *, category: str):
        try:
            target = os.path.join(self._clips_dir, category)
            fileutils.delete_directories(target)
            await reactions.confirmation(ctx.message)
        except Exception:
            await reactions.confusion(ctx.message)
            raise

    @commands.command()
    async def getclip(self, ctx, *, clip: str):
        path = await self.clip_path(clip)
        if path is None:
            await reactions.confusion(ctx.message)
            return
        await ctx.send(file=nextcord.File(path))

    @commands.command()
    async def addclip(self, ctx, folder: str, clip_name: str, *, url: str = None):
        if not await self._safe_path(folder):
            await reactions.confusion(ctx.message)
            return

        if not os.path.exists(os.path.join(self._clips_dir, folder)):
            try:
                os.makedirs(os.path.join(self._clips_dir, folder), exist_ok=True)
            except OSError:
                await reactions.confusion(ctx.message)
                raise

        if url is None or len(url) <= 0:
            # If no url was provided, then there has to be an audio attachment.
            if len(ctx.message.attachments) <= 0:
                await reactions.confusion(ctx.message)
                return
            url = ctx.message.attachments[0].url

        if not await self._valid_url(url):
            await reactions.confusion(ctx.message)
            return

        if '.' not in clip_name:
            clip_name += url[url.rfind('.'):]

        if not await self._valid_url(url):
            await reactions.confusion(ctx.message)
            return

        path = os.path.join(self._clips_dir, f'{folder}', clip_name.lower())
        try:
            with open(path, 'wb') as out_file:
                out_file.write(await webutils.url_get(url))
        except Exception:
            await reactions.confusion(ctx.message)
            raise

        await reactions.confirmation(ctx.message)

    @commands.command(aliases=['list'])
    async def clips(self, ctx, *, category: str = None):
        if category is None or category == 'all':
            categories = filter(lambda f: os.path.isdir(os.path.join(self._clips_dir, f)), os.listdir(self._clips_dir))
        else:
            categories = [os.path.join(self._clips_dir, category)]
            if not os.path.isdir(categories[0]):
                await reactions.confusion(ctx.message)
                return

        embed = nextcord.Embed(color=nextcord.Color(0xff0000))

        if category is None:  # List category names
            embed.title = '**Soundboard Categories**'
            embed.description = ' '.join([f'`{c}`' for c in categories])
        elif category == 'all':  # List all clips, sorted by category
            embed.title = '**Soundboard Clips**'
            for category in categories:
                field_value = ''

                for _, _, filenames in os.walk(os.path.join(self._clips_dir, category)):
                    field_value += ' '.join(
                        [f'`{f[:f.rfind(".")]}`' for f in filenames if self._is_audio_track(f)]
                    )

                if len(field_value) > 0:
                    embed.add_field(name=f'**{category}**', value=field_value)
        else:  # List clips within specific category
            embed.title = f'**{category} Clips**'.title()
            description = ''
            # List clips in specific category
            for _, _, filenames in os.walk(categories[0]):
                description += ' '.join([f'`{f[:f.rfind(".")]}`' for f in filenames if self._is_audio_track(f)])
            embed.description = description

        await ctx.send(embed=embed)

    def clip_names(self):
        clips = []
        for _, _, filenames in os.walk(self._clips_dir):
            clips.extend([f[:f.rfind('.')] for f in filenames if self._is_audio_track(f)])
        return clips

    async def clip_path(self, clip):
        for dirpath, _, filenames in os.walk(self._clips_dir):
            for file in filenames:
                if '.' in file and file[:file.rfind('.')] == clip:
                    return os.path.join(dirpath, file)
        return None

    ''' Begin private methods '''

    @staticmethod
    async def _safe_path(path):
        return path is not None and '..' not in path and not os.path.isabs(path)

    @staticmethod
    def _is_audio_track(filename):
        return type(filename) == str and '.' in filename

    @staticmethod
    async def _is_link(candidate):
        if type(candidate) != str:
            return False
        # Rudimentary link detection
        return candidate.startswith('https://') or candidate.startswith('http://') or candidate.startswith('www.')

    async def _valid_url(self, url):
        return url is not None and await self._is_link(url) and '.' in url


def setup(bot):
    bot.add_cog(SoundManager(bot))
