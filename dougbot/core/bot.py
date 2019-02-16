import asyncio
import os
import sys
import traceback

import discord.ext.commands
from discord.ext import commands

from dougbot.config import Config


class DougBot(discord.ext.commands.Bot):

    def __init__(self, config_file):
        self.config = Config(config_file)
        super().__init__(self.config.command_prefix)
        self._load_extensions()

    def run(self, *args, **kwargs):
        try:
            # Blocking function that does not return until the bot is done.
            print('Starting bot...')
            super().run(*(self.config.token, *args), **kwargs)
        except Exception as e:
            print(f'Uncaught exception while running bot: {e}')
            traceback.print_exc()
        finally:
            self.cleanup()

    # TODO FIX
    '''def say(self, *args, **kwargs):
        if args is None:
            return
        if len(args) > limits.MESSAGE_CHARACTER_LIMIT:
            self.whisper(args)
        else:
            super().say(args)'''

    async def on_ready(self):
        print('\nBot online')
        print(f'Name: {self.user.name}')
        print(f'ID: {self.user.id}')
        print('-' * (len(self.user.id) + len('ID: ')))

    async def on_command_error(self, ctx, error):
        if ctx is None or error is None:
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry, this command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)
        #await self.confusion(ctx.message)

    async def confusion(self, message):
        """
        Adds a question mark emoji to a user's message to indicate something went wrong in some way.
        :param message: The offending message
        """
        if message is not None:
            question_emoji = '\U00002753'
            await self.add_reaction(message, question_emoji)

    async def confirmation(self, message):
        if message is not None:
            ok_hand_emoji = '\U0001F44C'
            await self.add_reaction(message, ok_hand_emoji)

    '''async def send_message(self, destination, content=None, *, tts=False, embed=None):
        for shorter_message in long_message(content):
            await super().send_message(destination, content=shorter_message, tts=tts, embed=embed)
    '''

    async def join_channel(self, channel):
        if channel is None or channel.is_private:
            return None

        vc = self.voice_client_in(channel.server)

        if vc is not None and vc.channel == channel:
            return vc
        elif vc is not None:
            await self.leave_channel(vc.channel)

        # If there is a warning here, ignore it. Works perfectly fine
        return await self.join_voice_channel(channel)

    async def leave_channel(self, channel):
        if channel is None or channel.is_private:
            return

        vc = self.voice_client_in(channel.server)

        if vc is not None and vc.channel == channel:
            await vc.disconnect()

    async def be_terrible(self):

        pass

    def cleanup(self):
        if self.loop is not None and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.logout(), self.loop).result()

    def _load_extensions(self):
        exten_main_dir = os.path.dirname(os.path.dirname(__file__))
        exten_main_dir = os.path.join(exten_main_dir, 'extensions')

        # Add extension package to where the system looks for files.
        sys.path.append(exten_main_dir)

        for extension in os.listdir(exten_main_dir):
            if extension == 'example' or extension.endswith('.py'):
                continue

            extension_dir = os.path.join(exten_main_dir, extension)

            if os.path.isdir(extension_dir) and f'{extension}.py' in os.listdir(extension_dir):
                try:
                    self.load_extension(f'dougbot.extensions.{extension}.{extension}')
                except Exception:
                    print(f'Failed to load extension {extension}.', file=sys.stderr)
                    traceback.print_exc()


if __name__ == '__main__':
    dougbot = DougBot('../../config/config.ini')
    dougbot.run()
