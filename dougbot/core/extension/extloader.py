import os
import sys


class ExtensionLoader:

    @classmethod
    def load_extensions(cls, bot):
        exceptions = []
        if not os.path.exists(bot.EXTENSIONS_DIR):
            exceptions.append(Exception(f"Path to extensions, '{bot.EXTENSIONS_DIR},' does not exist."))
            return

        if bot.EXTENSIONS_DIR not in sys.path:
            sys.path.append(bot.EXTENSIONS_DIR)

        for root, _, files in os.walk(bot.EXTENSIONS_DIR):
            cls._load_from_package(bot, root, files, exceptions)

        return exceptions

    @classmethod
    def _load_from_package(cls, bot, root, files, exceptions):
        if not cls._is_extension_package(root):
            return

        for filename in files:
            cls._load_from_module(bot, root, filename, exceptions)

    @classmethod
    def _load_from_module(cls, bot, root, filename, exceptions):
        if not cls._is_extension_module(root, filename):
            return

        try:
            module_path = f'{root[len(bot.ROOT_DIR) + 1:]}.{filename[:-3]}'.replace(os.sep, '.')
            bot.load_extension(module_path)
        except Exception as e:
            # Ignore when there is no setup function. Can't know if it is an intentional issue or not.
            # If an extension SHOULD exist, but doesn't, this is likely the issue.
            if "no 'setup' function" not in str(e):
                exceptions.append(e)

    @staticmethod
    def _is_extension_module(path, filename):
        return os.path.basename(path) != 'extensions' and filename.endswith('.py') \
               and not (filename.startswith('__') or filename.startswith('example'))

    @staticmethod
    def _is_extension_package(path):
        return not (os.path.basename(path).startswith('__') or 'example' in path or 'util' in path or 'common' in path)
