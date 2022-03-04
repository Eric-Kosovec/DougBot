import os
import shutil

import nextcord

from dougbot.extensions.common import fileutils


class FileManager:

    def __init__(self, root):
        self._root = root

    async def get_file(self, path):
        target = await self._get_target(path)
        return nextcord.File(target) if os.path.isfile(target) else None

    async def list(self, path=None, sort=True):
        target = await self._get_target(path)

        files = os.listdir(target)
        if sort:
            files.sort()

        return files

    async def make_directory(self, directory):
        os.makedirs(await self._get_target(directory))

    async def make_file(self, path, data):
        target = await self._get_target(path)
        with open(target, 'wb') as fd:
            shutil.copyfileobj(data, fd)

    async def remove(self, path, force=False):
        target = await self._get_target(path)

        if os.path.isfile(target):
            os.remove(target)
        elif force:
            shutil.rmtree(target)
        else:
            os.removedirs(target)

    async def rename(self, from_path, to_path):
        source_path = await self._get_target(from_path)
        dest_path = await self._get_target(to_path)
        os.makedirs(dest_path, exist_ok=True)
        os.rename(source_path, dest_path)

    async def _get_target(self, path=None):
        if path is None:
            path = '.'

        return fileutils.PathBuilder(self._root) \
            .join(path) \
            .build()
