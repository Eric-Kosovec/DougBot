import os
import re


async def strip_traversals(path):
    if path is None:
        return None
    return path.replace(os.pardir, '')


class PathBuilder:

    def __init__(self, current=os.getcwd(), root=os.path.splitdrive(os.getcwd())[0]):
        self._current = current
        self._root = root

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
                    self._apply_path(file)
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

    def _apply_path(self, file):
        if file == os.curdir:
            return

        if file == os.pardir and self._current == self._root:
            self._done = True
            return

        if file == os.pardir:
            next_path = self._current[:-len(os.path.basename(self._current)) - 1]
        else:
            next_path = os.path.join(self._current, file)

        if not os.path.exists(next_path):
            self._done = True
            self._current = None
            return

        if os.path.isfile(next_path) and self._directory_only:
            self._done = True
            return

        self._current = next_path
        self._done = os.path.isfile(self._current)

        if self._combine_func is not None:
            self._combine_func(*(self._current, *self._args), **self._kwargs)

    @staticmethod
    def _under_root(path, root):
        # TODO
        return True
