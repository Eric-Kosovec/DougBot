import os
import sys
import traceback


class ExtensionLoader:
    EXTENSIONS_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'extensions')

    @staticmethod
    def load_extensions(client):
        if not os.path.exists(ExtensionLoader.EXTENSIONS_BASE):
            print(f"Path to extensions, '{ExtensionLoader.EXTENSIONS_BASE},' does not exist.", file=sys.stderr)
            return

        # Add extension package to where the system looks for files.
        if ExtensionLoader.EXTENSIONS_BASE not in sys.path:
            sys.path.append(ExtensionLoader.EXTENSIONS_BASE)

        for root, _, files in os.walk(ExtensionLoader.EXTENSIONS_BASE):
            if not ExtensionLoader._is_extension_package(root):
                continue

            for filename in files:
                if ExtensionLoader._is_extension_module(root, filename):
                    try:
                        client.load_extension(f'dougbot.extensions.{os.path.basename(root)}.{filename[:-3]}')
                    except Exception as e:
                        if "no 'setup' function" in str(e):
                            # Ignore when there is no setup function. Can't know if it is an intentional issue or not.
                            # If an extension SHOULD exist, but doesn't, this is likely the issue.
                            continue
                        print(f'\n{os.path.basename(root)}.{filename[:-3]} extension failed to load', file=sys.stderr)
                        traceback.print_exc()

    @staticmethod
    def _is_extension_module(path, filename):
        return os.path.basename(path) != 'extensions' and filename.endswith('.py') \
            and not (filename.startswith('__') or filename.startswith('example'))

    @staticmethod
    def _is_extension_package(path):
        return not (os.path.basename(path).startswith('__') or os.path.basename(path).startswith('example') or
                    os.path.basename(path).startswith('util') or os.path.basename(path).startswith('common'))
