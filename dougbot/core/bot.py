import asyncio
import inspect
import logging
import os
import traceback

from discord import TextChannel
from discord.ext import commands
from discord.utils import find

from dougbot.common.kvstore import KVStore
from dougbot.core.config import Config
from dougbot.core.db.dougbotdb import DougBotDB
from dougbot.core.extloader import ExtensionLoader
from dougbot.core.util.channelhandler import ChannelHandler


class DougBot(commands.Bot):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(os.path.dirname(ROOT_DIR))

    def __init__(self, token_file, config_file):
        # For notifying text channels the bot is online. Used to prevent spamming in case of shaky
        # internet, as on_ready can be called multiple times in such a case.
        self._on_ready_called = False
        self._log_channel = None
        self._config = Config(token_file, config_file)
        self._dougdb = DougBotDB()  # For core bot settings

        super().__init__(self._config.command_prefix, case_insensitive=True)
        ExtensionLoader.load_extensions(self)

    def run(self, *args, **kwargs):
        try:
            print("\nI'm starting...")
            super().run(*(self._config.token, *args), **kwargs)
        except Exception as e:
            print(f'FATAL EXCEPTION: Uncaught exception while running bot: {e}')
            traceback.print_exc()
        finally:
            print("I'm dying...")
            if self.loop is not None and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.logout(), self.loop)
            print("I've perished.")

    async def on_ready(self):
        if not self._on_ready_called:
            print('\nDoug Online')
            print(f'Name: {self.user.name}')
            print(f'ID: {self.user.id}')
            print('-' * (len(str(self.user.id)) + 4))

            self._log_channel = self.get_channel(self._config.logging_channel_id)
            if self._log_channel is not None:
                self._init_logging(self._log_channel)
            for text_channel in filter(lambda gc: isinstance(gc, TextChannel), self.get_all_channels()):
                if text_channel != self._log_channel:
                    await text_channel.send('I am sad.')
        self._on_ready_called = True

    async def on_command_error(self, ctx, error):
        if error is None or ctx is None:
            logger = logging.getLogger(__file__)
            logger.log(logging.ERROR, 'on_command_error got None argument')
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await self.confusion(ctx.message, f'Missing argument(s). Run {self._config.command_prefix}help <command_name>')
        if isinstance(error, commands.CheckFailure):
            await self.confusion(ctx.message, f'{ctx.author.mention} You do not have permissions for this command.')
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.message.channel.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.message.channel.send('This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):  # Catches rest of exceptions
            logger = logging.getLogger(__file__)
            logger.log(logging.ERROR, f'{error}\n{traceback.format_tb(error.original.__traceback__)}')

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

    # Per module KVStore
    async def kvstore(self):
        # TODO
        # DETERMINE CALLER EXTENSION
        # CREATE KVSTORE FOR EXTENSION, MAYBE CACHE THEM
        caller_stack = inspect.stack()[1]
        module = inspect.getmodule(caller_stack[0]).__name__
        module = module.replace('.', '_')
        return KVStore(self._dougdb, module)

    async def join_voice_channel(self, channel):
        if channel is not None:
            vc = find(lambda v: v.channel.id == channel.id, self.voice_clients)
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

    async def get_voice_in(self, channel):
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


if __name__ == '__main__':
    dougbot = DougBot('../../config/token', '../../config/config.ini')
    dougbot.run()
