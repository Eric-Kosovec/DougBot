import os
import re
import shutil


async def find_file_async(start_path, filename):
    return find_file(start_path, filename)


def find_file(start_path, filename):
    wanted_name, wanted_extension = os.path.splitext(filename)

    wanted_name = wanted_name.strip()
    wanted_extension = wanted_extension.strip()

    for path, _, files in os.walk(start_path):
        for file in files:
            name, extension = os.path.splitext(file)
            if wanted_name.lower() == name.lower() and (len(wanted_extension) == 0 or wanted_extension.lower() == extension.lower()):
                return os.path.join(path, file)

    return None


async def strip_traversals(path):
    if path is None:
        return None
    return path.replace(os.pardir, '')


def delete_directories(directory, ignore_errors=False, onerror=None):
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors, onerror)


class PathBuilder:

    def __init__(self, current, root=None):
        self._current = current
        self._root = current if root is None else root

        if not self._under_root(self._current, self._root):
            self._current = self._root

        self._done = os.path.isfile(self._current) or os.path.isfile(self._root)
        self._directory_only = False
        self._combine_func = None
        self._args = None
        self._kwargs = None

    def join(self, paths):
        if self._done:
            return self

        to_apply = [paths] if type(paths) == str else paths
        for path in to_apply:
            for file in re.split(r"[/\\]", path):
                if len(file) > 0:
                    self._done = self._apply_path(file)
                    if self._done:
                        return self

        return self

    def on_combine(self, func, *args, **kwargs):
        self._combine_func = func
        self._args = args
        self._kwargs = kwargs
        return self

    def directory_only(self):
        self._directory_only = True
        return self

    def build(self):
        return self._current

    def _apply_path(self, path):
        if path == os.curdir:
            return False

        is_parent_dir = path == os.pardir
        if is_parent_dir and self._current == self._root:
            return True

        if is_parent_dir:
            next_path = self._current[:-len(os.path.basename(self._current)) - 1]
        else:
            next_path = os.path.join(self._current, path)

        if os.path.exists(next_path) and os.path.isfile(next_path) and self._directory_only:
            return True

        self._current = next_path

        if self._combine_func is not None:
            self._combine_func(*(self._current, *self._args), **self._kwargs)

        return os.path.exists(self._current) and os.path.isfile(self._current)

    @staticmethod
    def _under_root(path, root):
        if '..' in path or os.path.islink(path):
            return False
        try:
            return os.path.commonpath([path, root]) == root
        except ValueError as _:
            return False


if __name__ == '__main__':
    pass
