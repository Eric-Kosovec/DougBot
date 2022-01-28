import os
import sys


class ExtensionLoader:

    @staticmethod
    def load_extensions(bot):
        exceptions = []
        extensions_dir = bot.EXTENSIONS_DIR

        if not os.path.exists(extensions_dir):
            exceptions.append(Exception(f"Path to extensions, '{extensions_dir},' does not exist."))
            return

        if extensions_dir not in sys.path:
            sys.path.append(extensions_dir)

        for root, _, files in os.walk(extensions_dir):
            if not ExtensionLoader._is_extension_package(root):
                continue

            for filename in files:
                if ExtensionLoader._is_extension_module(root, filename):
                    try:
                        module_path = os.path.join(root[len(bot.ROOT_DIR) + 1:], filename[:-3]).replace(os.sep, '.')
                        bot.load_extension(module_path)
                    except Exception as e:
                        if "no 'setup' function" in str(e):
                            # Ignore when there is no setup function. Can't know if it is an intentional issue or not.
                            # If an extension SHOULD exist, but doesn't, this is likely the issue.
                            continue
                        exceptions.append(e)

        return exceptions

    @staticmethod
    def _is_extension_module(path, filename):
        return os.path.basename(path) != 'extensions' and filename.endswith('.py') \
               and not (filename.startswith('__') or filename.startswith('example'))

    @staticmethod
    def _is_extension_package(path):
        # TODO CHECK FOR COMMON, UTIL, EXAMPLE BEING IN PATH
        return not (os.path.basename(path).startswith('__') or os.path.basename(path).startswith('example') or
                    os.path.basename(path).startswith('util') or os.path.basename(path).startswith('common'))
