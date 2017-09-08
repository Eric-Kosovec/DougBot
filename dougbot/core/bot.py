import asyncio
import os
import socket
import sys

import aiohttp
import discord.client
from discord import Message, Member

from dougbot.config import Config
from dougbot.core.exceptions.commanderror import CommandConflictError


# TODO LOGGING


class DougBot(discord.Client):
    def __init__(self, config_file):
        self.config = Config(config_file)
        self.plugins = self._load_plugins()
        # self.logger = get_logger()
        super().__init__()

    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.config.token))
        except discord.errors.LoginFailure:
            print('Bot could not login. Bad token.')
        except socket.gaierror:
            print('Bot could not login. Could not connect to Discord servers.')
        except aiohttp.errors.ClientOSError:
            print('Bot could not login. Could not connect to Discord servers.')
        finally:
            try:
                self._cleanup()
            except Exception as e:
                print('Cleanup error: %s', e)
            self.loop.close()

    async def on_ready(self):
        print('Bot online')
        print('Name: %s' % self.user.name)
        print('ID: %s' % self.user.id)
        print('-' * (len(self.user.id) + 4))

    # Occurs whenever a user changes their voice state
    async def on_voice_state_update(self, before: Member, after: Member):
        if before is None or after is None:
            return

        # They left a channel.
        if before.voice.voice_channel is not None and after.voice.voice_channel is None:
            voice_channel_left = before.voice.voice_channel
            bot_voice_client = self.voice_client_in(voice_channel_left.server)
            # No members left except possibly ourselves, so leave the channel if we are in there.
            if len(voice_channel_left.voice_members) == 1 and bot_voice_client is not None and bot_voice_client.channel == voice_channel_left:
                await self.voice_client_in(voice_channel_left.server).disconnect()

    async def on_message(self, message: Message):
        # Wait until the bot is ready before checking messages.
        await self.wait_until_ready()

        # Avoid any sort of bot talking to bot-type situation.
        if message.author.id == self.user.id or message.author.bot:
            return

        if not message.content.startswith(self.config.command_prefix):
            return

        (command, arguments) = self._parse_command(message.content, self.config.command_prefix)

        try:
            plugin = self.plugins[command]
            if plugin is None:
                await self.confusion(message)
            else:
                await plugin.run(command, message, arguments, self)
        except KeyError as e:  # Command not in dictionary.
            await self.confusion(message)
        except Exception as e:  # Catch any other errors that may occur.
            await self.confusion(message)
            print('Error occurred while running command: %s' % e)

    async def confusion(self, message):
        question_emoji = '❓'  # The Unicode string of the question emoji.
        await self.add_reaction(message, question_emoji)

    def _cleanup(self):
        try:
            self.loop.run_until_complete(self._logout())

            pending = asyncio.Task.all_tasks(self.loop)
            gathered = asyncio.gather(*pending, self.loop)

            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except:
            pass  # Ignore any exceptions

    async def _logout(self):
        await self._disconnect_voice_clients()
        await super().logout()

    async def _disconnect_voice_clients(self):
        for vc in self.voice_clients:
            await vc.disconnect()

    @staticmethod
    def _load_plugins():
        # Generate portable pathway to plugins
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        plugin_dir = os.path.join(plugin_dir, 'plugins')

        # Add plugin package to where the system looks for files.
        sys.path.append(plugin_dir)

        plugins = {}

        # Go through every file in the plugins folder
        for plugin in os.listdir(plugin_dir):
            if plugin.endswith('.py') and not plugin == 'example.py':
                plugin_name = plugin.split('.')[0].lower()
                # Import the plugin module
                prog = __import__(str(plugin_name))

                # If the plugin wants to be known by other names, use those names instead.
                if hasattr(prog, 'ALIASES') and len(prog.ALIASES) > 0:
                    for alias in prog.ALIASES:
                        norm_alias = alias.lower()

                        if norm_alias in plugins:
                            raise CommandConflictError(plugins[norm_alias], norm_alias)

                        plugins[norm_alias] = prog
                else:
                    if plugin_name in plugins:
                        raise CommandConflictError(plugins[plugin_name], plugin_name)
                    plugins[plugin_name] = prog

        sys.path.remove(plugin_dir)

        return plugins

    @staticmethod
    def _parse_command(message: str, prefix: str):
        if message is not None and prefix is not None and message.startswith(prefix):
            tokens = message.split()
            command = (tokens[0])[len(prefix):len(tokens[0])]  # Strip the prefix off the command
            arguments = tokens[1:len(tokens)]
        else:
            command = ''
            arguments = []

        return command, arguments

# TODO GRACEFUL HANDLING OF BEING KILLED FROM TERMINAL

if __name__ == '__main__':
    dougbot = DougBot('../config/config.ini')
    dougbot.run()
