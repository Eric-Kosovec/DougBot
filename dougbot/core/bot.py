import sys

import nextcord
from nextcord import Intents
from nextcord import Status
from nextcord.ext import commands
from nextcord.ext.commands import MinimalHelpCommand

from dougbot import config
from dougbot.common.logevent import LogEvent
from dougbot.common.messaging import reactions
from dougbot.core import extloader
from dougbot.core.log.channelhandler import ChannelHandler


class DougBot(commands.Bot):

    def __init__(self):
        self.config = config.get_configuration()
        self._is_ready = False

        intents = Intents(
            emojis_and_stickers=True,
            guilds=True,
            members=True,
            messages=True,
            presences=True,
            reactions=True,
            voice_states=True)

        bot_kwargs = {
            "intents": intents,
            "case_insensitive": True,
            "strip_after_prefix": True
        }

        super().__init__(self.config.command_prefix, **bot_kwargs)
        self._extension_load_errors = extloader.load_extensions(self)

    def run(self, *args, **kwargs):
        try:
            print("I'm starting...")
            super().run(*(self.config.token, *args), **kwargs)
        except Exception as e:
            LogEvent(__file__) \
                .message('Uncaught exception') \
                .exception(e) \
                .fatal()
            sys.exit(1)

    async def on_ready(self):
        if self._is_ready:
            return

        log_channel = await self.fetch_channel(self.config.logging_channel_id)
        if log_channel:
            LogEvent.add_handler(ChannelHandler(log_channel, self.loop))

        self.help_command = MinimalHelpCommand(no_category='Misc')

        for error in self._extension_load_errors:
            LogEvent(__file__) \
                .exception(error) \
                .error(to_console=True)

        print('Doug Online')

        self._is_ready = True

    async def close(self):
        if self.loop and self.loop.is_running():
            await self.change_presence(status=Status.offline)
            await super().close()

    async def on_error(self, event_method, *args, **kwargs):
        pass

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
        LogEvent(__file__) \
            .exception(error) \
            .error()

        await reactions.check_log(ctx.message)

    async def join_voice_channel(self, channel):
        voice_client = await self.voice_in(channel)
        return await channel.connect() if voice_client is None else voice_client

    async def voice_in(self, channel):
        return nextcord.utils.find(lambda vc: vc.channel.id == channel.id, self.voice_clients)
