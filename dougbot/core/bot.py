import asyncio
import os
import signal
import sys
import time
from typing import Any

from discord import Intents, Interaction, ApplicationCommandError
from discord import Status
from discord.ext import commands

from dougbot import config
from dougbot.common.alogger import AsyncLogger
from dougbot.common.logger import Logger
from dougbot.common.messaging import reactions
from dougbot.core import extloader
from dougbot.core.help import CustomHelpCommand
from dougbot.core.log.async_channel_handler import AsyncChannelHandler
from dougbot.core.log.channelhandler import ChannelHandler


class DougBot(commands.Bot):

    def __init__(self):
        self.config = config.get_configuration()
        self._log_channel = None

        self._attempt_run = True

        bot_kwargs = {
            "intents": Intents.all(),
            "case_insensitive": True,
            "strip_after_prefix": True
        }

        self._create_signal_handler()

        super().__init__(self.config.command_prefix, **bot_kwargs)
        self._extension_load_errors = extloader.load_extensions(self)

    def run(self, token: str = None, *, reconnect: bool = True):
        if not self.config.token:
            print("Token doesn't exist; check your environment variables", file=sys.stderr)
            sys.exit(1)

        while self._attempt_run:
            print("I'm starting...")

            try:
                super().run(self.config.token, reconnect=reconnect)
                self._attempt_run = False
            except Exception as e:
                print(f'Failed to run: {e}', file=sys.stderr)

                # Create a new loop, as the superclass closes the old one and only grabs a new one in the constructor
                self.loop = asyncio.new_event_loop()

                time.sleep(self.config.run_attempt_cooldown_secs)

    async def on_connect(self):
        await AsyncLogger.start()

        # TODO DOES THIS METHOD RUN ONCE? IF NO, THEN HANDLER WILL NEED TO BE THOUGHT ABOUT MORE
        self._log_channel = await self.fetch_channel(self.config.logging_channel_id)
        if self._log_channel:
            await AsyncLogger.set_handler(AsyncChannelHandler(self._log_channel))

        self.help_command = CustomHelpCommand(dm_help=None, no_category='Misc')

        print('Doug Online')

    async def on_ready(self):
        # Log errors that occurred while bot was down
        if self._log_channel:
            asyncio.create_task(AsyncLogger.log_pending())

        for error in self._extension_load_errors:
            asyncio.create_task(AsyncLogger.error(
                __file__, message='Error while loading extension', exception=error, to_console=True))

        self._extension_load_errors.clear()

    async def close(self):
        # TODO CHECK THIS WORKS
        if await self.has_connection():
            await self.change_presence(status=Status.offline)

            for vc in self.voice_clients:
                await vc.disconnect(force=True)

        # TODO MAKE SURE THIS WORKS
        await AsyncLogger.close()

        await super().close()

    async def on_error(self, event_method, *args, **kwargs):
        _, exception, _ = sys.exc_info()
        Logger(__file__) \
            .method(event_method) \
            .add_field('arguments', args) \
            .add_field('keyword_arguments', kwargs) \
            .exception(exception) \
            .error()

    async def on_application_command_error(self, interaction: Interaction, exception: ApplicationCommandError):
        Logger(__file__) \
            .message('Error executing command') \
            .interaction(interaction) \
            .exception(exception) \
            .error()

        await reactions.check_log(interaction.message)

    async def on_command_error(self, ctx, exception):
        Logger(__file__) \
            .message('Error executing command') \
            .context(ctx) \
            .exception(exception) \
            .error()

        await reactions.check_log(ctx.message)

    async def has_connection(self):
        return self.ws and not self.is_closed()

    def get_cog(self, name: str) -> Any:
        """
        Override commands.Bot get_cog to eliminate dumb warnings when type hinting the return
        :param name: Class name of Cog
        :return: Cog instance
        """
        return super().get_cog(name)

    def _create_signal_handler(self):
        def signal_handler(_, __):
            if self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self.close(), self.loop)
            else:
                sys.exit(1)

        if os.name != 'nt':  # Linux
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGILL, signal_handler)
        else:
            signal.signal(signal.SIGBREAK, signal_handler)

        signal.signal(signal.SIGINT, signal_handler)
