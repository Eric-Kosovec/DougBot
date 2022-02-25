import inspect
import logging
import os
import sys
import traceback

import nextcord.utils
from nextcord import Intents
from nextcord import Status
from nextcord.ext import commands

from dougbot.common.data.database import Database
from dougbot.common.data.kvstore import KVStore
from dougbot.common.messaging import reactions
from dougbot.core.configure.config import Config
from dougbot.core.extension.extloader import ExtensionLoader
from dougbot.core.logger.channelhandler import ChannelHandler


class DougBot(commands.Bot):

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTENSIONS_DIR = os.path.join(ROOT_DIR, 'dougbot', 'extensions')
    RESOURCES_DIR = os.path.join(ROOT_DIR, 'resources', 'dougbot', 'extension')

    def __init__(self):
        self._config = Config(os.path.join(self.ROOT_DIR, 'resources', 'config'))
        self._database = Database(os.path.join(self.ROOT_DIR, 'resources', 'dougbot', 'core', 'db', 'dougbot.db'))  # For core bot settings
        self._log_channel = None

        # Prevent on_ready from initializing data multiple times
        self._ready_finished = False

        bot_kwargs = {
            "intents": Intents.all(),  # TODO More specific intents
            "case_insensitive": True,
            "strip_after_prefix": True
        }

        super().__init__(self._config.command_prefix, **bot_kwargs)
        self._extension_load_errors = ExtensionLoader.load_extensions(self)

    def run(self, *args, **kwargs):
        try:
            print("I'm starting...")
            super().run(*(self._config.token, *args), **kwargs)
        except Exception as e:
            print(f'\nFATAL EXCEPTION: Uncaught exception while running bot: {e}', file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

    async def on_ready(self):
        if self._ready_finished:
            return

        print('\nDoug Online')
        print('-----------')

        self._log_channel = self.get_channel(self._config.logging_channel_id)
        if self._log_channel is not None:
            logging.getLogger('').addHandler(ChannelHandler(self._log_channel, self.loop))

        for error in self._extension_load_errors:
            logging.getLogger(__file__).log(logging.ERROR, f'{error}\n{"".join(traceback.format_tb(error.__traceback__))}')

        self._ready_finished = True

    async def close(self):
        await self.change_presence(status=Status.offline)
        await super().close()

    async def on_command_error(self, ctx, error):
        error_texts = {
            commands.errors.MissingRequiredArgument: f'Missing argument(s), type {ctx.prefix}help <command_name>',
            commands.errors.CheckFailure: f'{ctx.author.mention} You do not have permissions for this command',
            commands.errors.NoPrivateMessage: 'Command cannot be used in private messages',
            commands.errors.DisabledCommand: 'Command disabled and cannot be used',
            commands.errors.CommandNotFound: 'Command not found',
            commands.errors.CommandOnCooldown: 'Command on cooldown'
        }

        for error_class, error_msg in error_texts.items():
            if isinstance(error, error_class):
                await reactions.confusion(ctx.message, error_msg)
                return

        # Catches rest of exceptions
        logging.getLogger(__file__).log(logging.ERROR, f'{error}\n{" ".join(traceback.format_tb(error.original.__traceback__))}')
        await reactions.check_log(ctx.message)

    # Sibling module is a Python file within the same package as the caller, unless caller is a core or admin module.
    def kv_store(self, sibling_module=None):
        caller_stack = inspect.stack()[1]
        calling_module = inspect.getmodule(caller_stack[0]).__name__

        if sibling_module is not None:
            sibling_module = sibling_module.replace(os.sep, '.')
            extension_package = 'dougbot.extensions'
            if not sibling_module.startswith(extension_package):
                sibling_module = f'{extension_package}.{sibling_module}'

            if not self._is_admin_package(calling_module) and not self._same_extension_package(calling_module, sibling_module):
                raise ValueError(f"Cannot get sibling module '{sibling_module}' from '{calling_module}'")

        return KVStore(self._database, calling_module.replace('.', '_'))

    async def join_voice_channel(self, channel):
        voice_client = await self.get_voice(channel)
        return await channel.connect() if voice_client is None else voice_client

    @staticmethod
    async def leave_voice_channel(voice):
        if voice is not None:
            await voice.disconnect()

    async def in_voice_channel(self, channel):
        return await self.get_voice(channel) is not None

    async def get_voice(self, channel):
        return nextcord.utils.find(lambda vc: vc.channel.id == channel.id, self.voice_clients)

    async def log_channel(self):
        return self._log_channel

    def admin_role_id(self):
        return self._config.admin_role_id

    ''' PRIVATE METHODS '''

    @staticmethod
    def _same_extension_package(main_module, sibling_module):
        extension_package = 'dougbot.extension'
        i = len(extension_package) + 1 if main_module.startswith(extension_package) else 0
        j = len(extension_package) + 1 if sibling_module.startswith(extension_package) else 0

        while i < len(main_module) and j < len(sibling_module):
            if main_module[i] != sibling_module[j]:
                return False
            if main_module[i] == sibling_module[j] == '.':
                return True
            i += 1
            j += 1

        return False

    @staticmethod
    def _is_admin_package(module):
        return module.startswith(f'dougbot.core') or module.startswith(f'dougbot.extensions.admin')


if __name__ == '__main__':
    DougBot().run()
