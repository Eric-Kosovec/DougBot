import asyncio
import os
import sys
import traceback

from discord.ext import commands
from discord.utils import find

from dougbot.config import Config
from dougbot.core.extloader import ExtensionLoader


class DougBot(commands.Bot):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(os.path.dirname(ROOT_DIR))

    def __init__(self, config_file):
        self.config = Config(config_file)
        super().__init__(self.config.command_prefix, case_insensitive=True)
        ExtensionLoader.load_extensions(self)

    def run(self, *args, **kwargs):
        try:
            print("\nI'm starting...")
            super().run(*(self.config.token, *args), **kwargs)
        except Exception as e:
            print(f'Uncaught exception while running bot: {e}')
            traceback.print_exc()
        finally:
            print("I'm dying...")
            if self.loop is not None and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.logout(), self.loop).result()
            print("I've perished.")

    async def on_ready(self):
        print('\nDoug Online')
        print(f'Name: {self.user.name}')
        print(f'ID: {self.user.id}')
        print('-' * (len(str(self.user.id)) + 4))

    async def on_command_error(self, ctx, error):
        if error is None or ctx is None:
            print('Error: on_command_error got None argument.', file=sys.stderr)
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await self.confusion(ctx.message, f'Missing argument(s). Run {self.config.command_prefix}help <command_name>')
        if isinstance(error, commands.CheckFailure):
            await self.confusion(ctx.message, f'{ctx.author.mention} You do not have permissions for this command.')
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


if __name__ == '__main__':
    dougbot = DougBot('../../config/config.ini')
    dougbot.run()
