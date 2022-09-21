import os
import shutil

import cachetools


class FileManager:

    def __init__(self, root):
        self._root = os.path.normpath(root)
        self._path_cache = cachetools.LRUCache(maxsize=20)

    async def find_file(self, filename, *, relative=True):
        if filename in self._path_cache:
            cached_path = self._path_cache[filename]
            return await self._to_relative_path(cached_path) if relative else cached_path

        # TODO ANYWAY TO DO AN ASYNC WALK?
        for root, _, files in os.walk(self._root):
            for file in files:
                if filename == os.path.splitext(file)[0]:
                    absolute_path = os.path.join(root, file)

                    self._path_cache[filename] = absolute_path

                    if relative:
                        return await self._to_relative_path(absolute_path)

                    return absolute_path

        return None

    async def list(self, path=None, *, sort=False):
        target = await self._get_target(path) if path else self._root
        if not target:
            return None

        files = os.listdir(target)
        return files.sort() if sort else files

    async def walk(self, path):
        file_list = []
        for root, _, files in os.walk(await self._get_target(path)):
            file_list.extend([os.path.join(root, file) for file in files])
        return file_list

    async def make_directory(self, directory):
        target = await self._get_target(directory)
        if not target:
            return False

        os.makedirs(target, exist_ok=True)
        return True

    async def make_file(self, path, data):
        target = await self._get_target(path)
        if not target:
            return False

        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'wb') as fd:
            fd.write(data)

        return True

    async def copy(self):
        pass

    async def remove(self, path, force=False):
        target = await self._get_target(path)
        if not target:
            return False

        if os.path.isfile(target):
            os.remove(target)
            await self._delete_from_cache(target)
        elif force:
            shutil.rmtree(target)
        else:
            os.removedirs(target)

        return True

    async def rename(self, from_path, to_path):
        source_path = await self._get_target(from_path)
        if not source_path:
            return False

        dest_path = await self._get_target(to_path)
        if not dest_path:
            return False

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        os.rename(source_path, dest_path)

        if os.path.isfile(dest_path):
            await self._delete_from_cache(dest_path)

        return True

    async def _get_target(self, path):
        target_path = path if path.startswith(self._root) else os.path.join(self._root, path)
        return target_path if await self._is_valid_path(target_path) else None

    async def _is_valid_path(self, path):
        return path and os.path.realpath(path).startswith(self._root)

    async def _to_relative_path(self, path):
        relative_path = path.replace(self._root, "")
        if len(relative_path) > 0 and relative_path[0] in '/\\':
            return relative_path[1:]
        return relative_path

    async def _delete_from_cache(self, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        if filename in self._path_cache:
            del self._path_cache[filename]
