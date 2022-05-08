import os

from dougbot.config import EXTENSIONS_DIR, ROOT_DIR


def load_extensions(bot):
    if not os.path.exists(EXTENSIONS_DIR):
        return [Exception(f"Path to extensions '{EXTENSIONS_DIR}' does not exist")]

    exceptions = []

    for root, _, files in os.walk(EXTENSIONS_DIR):
        _load_from_package(bot, root, files, exceptions)

    return exceptions


def _load_from_package(bot, root, files, exceptions):
    if not _is_extension_package(root):
        return

    for filename in files:
        _load_from_module(bot, root, filename, exceptions)


def _load_from_module(bot, root, filename, exceptions):
    if not _is_extension_module(root, filename):
        return

    module_path = f'{root[len(ROOT_DIR) + 1:]}.{filename[:-3]}'.replace(os.sep, '.')
    try:
        bot.load_extension(module_path)
    except Exception as e:
        # Ignore when there is no setup function. Can't know if it is an intentional issue or not.
        # If an extension SHOULD exist, but doesn't, this is likely the issue.
        if "no 'setup' function" not in str(e):
            exceptions.append(e)


def _is_extension_module(path, filename):
    return os.path.basename(path) != 'extensions' and filename.endswith('.py') \
           and not (filename.startswith('__') or filename.startswith('example'))


def _is_extension_package(path):
    return not (os.path.basename(path).startswith('__') or 'example' in path or 'util' in path or 'common' in path)
