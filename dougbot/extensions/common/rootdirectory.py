import os


class RootDirectory:

    # TODO COMMENT ON HOW IT WORKS
    # TODO MAKE ASYNC

    # TODO HANDLE ROOT INITIALLY HAVING ..
    #   PATH NORMALIZATION IF . IN GIVEN PATH FOR OTHER METHODS?
    # Root must be the full path on the drive.
    def __init__(self, root):
        self._root = root

    def root(self):
        return self._root

    def file_exists(self, filename, directory=None):
        return self.find_file(filename, directory) is not None

    def dir_exists(self, directory):
        if directory is None:
            return False
        path = os.path.join(self.root(), directory)
        return self._is_under_root(path) and os.path.isdir(path)

    def find_file(self, filename, directory=None):
        if filename is None:
            return None

        search_dir = self.root()
        if directory is not None:
            search_dir = os.path.join(search_dir, directory)

        if not self._is_under_root(search_dir):
            return None

        has_ext = len(os.path.splitext(filename)[-1]) > 1  # Extension comes out to more than '.'

        for path, _, files in os.walk(search_dir):
            if has_ext and filename in files:
                return self.relative_path(os.path.join(path, filename))
            elif not has_ext:
                for file in files:
                    if filename == os.path.splitext(file)[0]:
                        return self.relative_path(os.path.join(path, file))

        return None

    def create_file(self, path):
        full_path = os.path.join(self.root(), path)
        if not self._is_under_root(full_path):
            return False
        open(full_path, 'w').close()
        return True

    def rename_file(self, src, dst):
        src_abs = self.absolute_path(src)
        dst_abs = self.absolute_path(dst)
        os.rename(src_abs, dst_abs)

    def move_file(self, src, dst):
        src_abs = self.absolute_path(src)
        dst_abs = self.absolute_path(dst)
        if not os.path.exists(dst_abs):
            os.makedirs(dst_abs, exist_ok=True)
        os.rename(src_abs, dst_abs)

    def absolute_path(self, path):
        if path is None:
            return None
        if os.path.isabs(path):
            return path
        return os.path.join(self.root(), path)

    def relative_path(self, path):
        # TODO DETECT WHEN PATH IS ALREADY RELATIVE
        if path is None:
            return None
        if not self._is_under_root(path):
            return None
        common_path = os.path.commonpath([path, self.root()])
        return path[len(common_path) + 1:]  # + 1 to skip past the '\' character

    def list_files(self):
        all_files = []
        for path, _, files in os.walk(self.root()):
            all_files.extend([self.relative_path(os.path.join(path, file)) for file in files])
        return all_files

    def list_dirs(self):
        all_dirs = []
        for path, dirs, _ in os.walk(self.root()):
            all_dirs.extend([self.relative_path(os.path.join(path, directory)) for directory in dirs])
        return all_dirs

    def delete_file(self, filename, directory=None):
        if filename is None:
            return False

        search_dir = self.root()
        if directory is not None:
            search_dir = os.path.join(search_dir, directory)

        if not self._is_under_root(search_dir):
            return False

        has_ext = len(os.path.splitext(filename)[-1]) > 1

        for path, _, files in os.walk(search_dir):
            if has_ext and filename in files:
                os.remove(os.path.join(path, filename))
                return True
            elif not has_ext:
                for file in files:
                    if filename == os.path.splitext(file)[0]:
                        os.remove(os.path.join(path, file))
                        return True

        return False

    def delete_dir(self, directory):
        if directory is None:
            return
        path = os.path.join(self.root(), directory)
        if not self._is_under_root(path):
            return False
        os.rmdir(path)
        return True

    # No parent directory traversals, i.e., '..'
    # No symbolic links
    def _is_under_root(self, path):
        if path is None or '..' in path or os.path.islink(path):
            return False
        if os.path.splitdrive(path)[0] != os.path.splitdrive(self.root())[0] or \
                os.path.commonpath([path, self.root()]) != self.root():
            return False
        return True
