import os
import sys


class ExtensionLoader:
    _extensions_base = os.path.dirname(os.path.dirname(__file__))
    _extensions_base = os.path.join(_extensions_base, 'extensions')

    @classmethod
    def load_extensions(cls, client):
        if not os.path.exists(cls._extensions_base):
            print(f"Path to extensions, '{cls._extensions_base},' does not exist.", file=sys.stderr)
            return

        # Add extension package to where the system looks for files.
        if cls._extensions_base not in sys.path:
            sys.path.append(cls._extensions_base)

        for root, _, files in os.walk(cls._extensions_base):
            if not cls._is_extension_package(root):
                continue

            for filename in files:
                if cls._is_extension_module(root, filename):
                    try:
                        client.load_extension(f'dougbot.extensions.{os.path.basename(root)}.{filename[:-3]}')
                    except Exception as e:
                        no_setup_func = "no 'setup' function"
                        if no_setup_func in str(e):
                            # Ignore when there is no setup function. Can't know if it is an intentional issue or not.
                            continue
                        print(f'{os.path.basename(root)}.{filename[:-3]} extension failed to load: {e}',
                              file=sys.stderr)

    @staticmethod
    def _is_extension_module(path, filename):
        if path is None or filename is None:
            return False
        return os.path.basename(path) != 'extensions' and filename.endswith('.py') \
            and not (filename.startswith('__') or filename.startswith('example'))

    @staticmethod
    def _is_extension_package(path):
        if path is None:
            return False
        return not (os.path.basename(path).startswith('__') or os.path.basename(path).startswith('example') or
                    os.path.basename(path).startswith('util'))
