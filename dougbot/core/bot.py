import asyncio
import os
import sys
import traceback

import discord.ext.commands
from discord.channel import TextChannel
from discord.ext import commands

from dougbot.config import Config


class DougBot(commands.AutoShardedBot):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(os.path.dirname(ROOT_DIR))

    def __init__(self, config_file):
        self.config = Config(config_file)
        super().__init__(self.config.command_prefix, case_insensitive=True)
        self._load_extensions()

    def run(self, *args, **kwargs):
        try:
            print("\nI'm starting...")
            # Blocking function that does not return until the bot is done.
            super().run(*(self.config.token, *args), **kwargs)
        except Exception as e:
            print(f'Uncaught exception while running bot: {e}')
            traceback.print_exc()
        finally:
            print("I'm dying...")
            self.cleanup()

    async def on_ready(self):
        print('\nDoug Online')
        print(f'Name: {self.user.name}')
        print(f'ID: {self.user.id}')
        print('-' * (len(str(self.user.id)) + 4))
        for text_channel in filter(lambda gc: isinstance(gc, TextChannel), self.get_all_channels()):
            await text_channel.send('I am sad.')

    async def on_command_error(self, ctx, error):
        print('PRINTING ERROR')
        print(error)
        # TODO EXPAND
        if error is None or ctx is None:
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await self.confusion(ctx.message, 'Missing required argument.')
        if isinstance(error, commands.CheckFailure):
            await self.confusion(ctx.message, 'You do not have permissions for this command.')
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.message.channel.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.message.channel.send('This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            traceback.print_tb(error.original.__traceback__)

    @staticmethod
    async def confusion(message, error_msg=None):
        if message is not None:
            question_emoji = '\U00002753'
            await message.add_reaction(question_emoji)

            if error_msg is not None:
                await message.channel.send(error_msg)

    @staticmethod
    async def confirmation(message, confirm_msg=None):
        if message is not None:
            ok_hand_emoji = '\U0001F44C'
            await message.add_reaction(ok_hand_emoji)

            if confirm_msg is not None:
                await message.channel.send(confirm_msg)

    @staticmethod
    async def join_channel(channel):
        if channel:
            return await channel.connect()
        return None

    @staticmethod
    async def leave_channel(voice):
        if voice:
            await voice.disconnect()

    def cleanup(self):
        if self.loop is not None and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.logout(), self.loop).result()
            self.loop.stop()
            self.loop.close()
            self.loop = None

    def _load_extensions(self):
        extensions_base = os.path.dirname(os.path.dirname(__file__))
        extensions_base = os.path.join(extensions_base, 'extensions')

        if not os.path.exists(extensions_base):
            print(f"Path to extensions, '{extensions_base},' does not exist.", file=sys.stderr)
            return

        # Add extension package to where the system looks for files.
        if extensions_base not in sys.path:
            sys.path.append(extensions_base)

        for dirpath, dirnames, filenames in os.walk(extensions_base):
            if not self._is_extension_package(dirpath):
                continue

            for filename in filenames:
                if self._is_extension_module(dirpath, filename):
                    try:
                        self.load_extension(f'dougbot.extensions.{os.path.basename(dirpath)}.{filename[:-3]}')
                    except discord.ClientException:
                        print(f'{os.path.basename(dirpath)}.{filename[:-3]} has no setup function.')
                    except Exception as e:
                        print(f'{os.path.basename(dirpath)}.{filename[:-3]} extension failed to load: {e}',
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


if __name__ == '__main__':
    dougbot = DougBot('../../config/config.ini')
    dougbot.run()
