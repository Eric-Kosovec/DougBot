import asyncio
import os
import signal
import sys
from typing import Any

from nextcord import ApplicationError, Intents, Interaction
from nextcord import Status
from nextcord.ext import commands

from dougbot import config
from dougbot.common.logger import Logger
from dougbot.common.messaging import reactions
from dougbot.core import extloader
from dougbot.core.help import CustomHelpCommand
from dougbot.core.log.channelhandler import ChannelHandler


class DougBot(commands.Bot):

    def __init__(self):
        self.config = config.get_configuration()
        self._log_channel = None

        bot_kwargs = {
            "intents": Intents.all(),
            "case_insensitive": True,
            "strip_after_prefix": True
        }

        self._create_signal_handler()

        super().__init__(self.config.command_prefix, **bot_kwargs)
        self._extension_load_errors = extloader.load_extensions(self)

    def run(self, *args, **kwargs):
        if not self.config.token:
            print("Token doesn't exist; check your environment variables", file=sys.stderr)
            sys.exit(1)

        try:
            print("I'm starting...")
            super().run(*(self.config.token, *args), **kwargs)
        except Exception as e:
            Logger(__file__) \
                .message('Uncaught exception') \
                .exception(e) \
                .fatal()

            sys.exit(1)

    async def on_connect(self):
        self._log_channel = await self.fetch_channel(self.config.logging_channel_id)
        if self._log_channel:
            Logger.add_handler(ChannelHandler(config.ROOT_DIR, self._log_channel, self.loop))

        self.help_command = CustomHelpCommand(dm_help=None, no_category='Misc')

        print('Doug Online')

    async def on_ready(self):
        # Log errors that occurred while bot was down
        if self._log_channel:
            Logger.log_fatal_file()

        for error in self._extension_load_errors:
            Logger(__file__) \
                .message('Error while loading extension') \
                .exception(error) \
                .error(to_console=True)

        self._extension_load_errors.clear()

    async def close(self):
        await self.change_presence(status=Status.offline)
        
        for vc in self.voice_clients:
            await vc.disconnect(force=True)

        # TODO FINISH LOGGING

        await super().close()

    async def on_error(self, event_method, *args, **kwargs):
        _, exception, _ = sys.exc_info()
        Logger(__file__) \
            .method(event_method) \
            .add_field('arguments', args) \
            .add_field('keyword_arguments', kwargs) \
            .exception(exception) \
            .error()

    async def on_application_command_error(self, interaction: Interaction, exception: ApplicationError):
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

        if os.name != 'nt':  # Windows
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGILL, signal_handler)
        else:
            signal.signal(signal.SIGBREAK, signal_handler)

        signal.signal(signal.SIGINT, signal_handler)
