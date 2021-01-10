import asyncio
import inspect
import logging
import os
import sys
import traceback

import discord
from discord.ext import commands
from discord.utils import find

from dougbot.common.kvstore import KVStore
from dougbot.core.config import Config
from dougbot.core.db.dougbotdb import DougBotDB
from dougbot.core.extloader import ExtensionLoader
from dougbot.core.util.channelhandler import ChannelHandler


class DougBot(commands.Bot):
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def __init__(self, token_file, config_file):
        # For notifying text channels the bot is online. Used to prevent spamming in case of shaky
        # internet, as on_ready can be called multiple times in such a case.
        self._on_ready_called = False
        self._log_channel = None
        self._config = Config(token_file, config_file)
        self._dougdb = DougBotDB()  # For core bot settings

        intent = discord.Intents.default()
        intent.members = True
        intent.presences = True

        super().__init__(self._config.command_prefix, intents=intent, case_insensitive=True)
        ExtensionLoader.load_extensions(self)

    def run(self, *args, **kwargs):
        try:
            self._on_ready_called = False
            print("\nI'm starting...")
            super().run(*(self._config.token, *args), **kwargs)
        except Exception as e:
            print(f'\nFATAL EXCEPTION: Uncaught exception while running bot: {e}', file=sys.stderr)
            traceback.print_exc()
        finally:
            print("\nI'm dying...", file=sys.stderr)
            if self.loop is not None and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.logout(), self.loop)
            print("\nI've perished.", file=sys.stderr)

    async def on_ready(self):
        if not self._on_ready_called:
            print('\nDoug Online')
            print(f'Name: {self.user.name}')
            print(f'ID: {self.user.id}')
            print('-' * (len(str(self.user.id)) + 4))

            self._log_channel = self.get_channel(self._config.logging_channel_id)
            if self._log_channel is not None:
                self._init_logging(self._log_channel)
                await self._log_channel.send('I am sad.')

            self._on_ready_called = True

    async def on_command_error(self, ctx, error):
        if ctx is None or error is None:
            logger = logging.getLogger(__file__)
            logger.log(logging.ERROR, 'on_command_error got None argument(s)')
            return

        error_texts = {
            commands.errors.MissingRequiredArgument: f'Missing argument(s), type {self._config.command_prefix}help <command_name>',
            commands.errors.CheckFailure: f'{ctx.author.mention} You do not have permissions for this command.',
            commands.errors.NoPrivateMessage: 'Command cannot be used in private messages.',
            commands.errors.DisabledCommand: 'Command disabled and cannot be used.',
            commands.errors.CommandNotFound: 'Command not found.',
            commands.errors.CommandOnCooldown: 'Command on cooldown.',
        }

        for error_class, error_msg in error_texts.items():
            if isinstance(error, error_class):
                await self.confusion(ctx.message, error_msg)
                return

        if isinstance(error, commands.CommandInvokeError):  # Catches rest of exceptions
            logger = logging.getLogger(__file__)
            logger.log(logging.ERROR, f'{error}\n{traceback.format_tb(error.original.__traceback__)}')
            await self.check_log(ctx.message)

    @staticmethod
    async def check_log(message, error_msg=None):
        if message is not None:
            page_emoji = '📄'
            await message.add_reaction(page_emoji)
            if error_msg is not None:
                await message.channel.send(error_msg)

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

    # Per module KVStore - Must not be asynchronous as to allow being called from __init__s.
    def kv_store(self, sibling_module=None):
        caller_stack = inspect.stack()[1]
        module = inspect.getmodule(caller_stack[0]).__name__

        #print(module)
        #print(sibling_module)

        #self._is_same_package(module, sibling_module)

        #if sibling_module is not None:
        #    # TODO MAKE SURE UNDER SAME PACKAGE
        #    pass
        #else:
        module = module.replace('.', '_')
        return KVStore(self._dougdb, module)

    async def join_voice_channel(self, channel):
        if channel is not None:
            vc = await self.get_voice(channel)
            return vc if vc is not None else await channel.connect()
        return None

    @staticmethod
    async def leave_voice_channel(voice):
        if voice is not None:
            await voice.disconnect()

    async def in_voice_channel(self, channel):
        if channel is not None:
            return find(lambda vc: vc.channel.id == channel.id, self.voice_clients) is not None
        return False

    async def get_voice(self, channel):
        if channel is not None:
            return find(lambda vc: vc.channel.id == channel.id, self.voice_clients)
        return None

    async def log_channel(self):
        return self._log_channel

    def get_config(self):
        return self._config

    ''' Begin private methods '''

    def _init_logging(self, channel):
        if channel is not None and self.loop is not None:
            # Add the custom handler to the root logger, so it applies to every time logging is called.
            logging.getLogger('').addHandler(ChannelHandler(self.ROOT_DIR, channel, self.loop))

    def _is_same_package(self, main_module: str, sibling_module: str):
        module_prefix = 'dougbot.extensions'
        #print(main_module)
        prefix_packages = main_module[:main_module.rfind('.')]

        if not sibling_module.startswith(prefix_packages):
            sibling_module = f'{prefix_packages}.{sibling_module}'

        # If it exists, then same, otherwise not
        #importlib

        # TODO

        #print(prefix_packages)
        return True


if __name__ == '__main__':
    dougbot = DougBot('../../config/token', '../../config/config.ini')
    dougbot.run()
