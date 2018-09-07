import asyncio
import importlib
import inspect
import os
import sys

import discord.client

from dougbot.config import Config
from dougbot.core.command import CommandEvent, CommandError
from dougbot.core.commandparser import CommandParser
from dougbot.plugins.plugin import Plugin


class DougBot(discord.Client):

    def __init__(self, config_file):
        super().__init__()
        self.config = Config(config_file)
        self.command_prefix = self.config.command_prefix

        # TODO PROTECT SYSTEM DIRECTORIES FROM PLUGINS - CROSS-PLATFORM

        self._plugins = self._load_plugins()  # Dictionary of plugin name to Plugin class instance
        self._commands = self._command_list()
        self._listeners = self._listener_list()
        self._command_parser = CommandParser(self._commands)

    def run(self, *args, **kwargs):
        try:
            # Blocking function that does not return until the bot is done.
            print('Starting bot...')
            super().run(*(self.config.token, *args), **kwargs)
        except Exception as e:
            print(f'Exception while running bot: {e}')
        finally:
            self.cleanup()

    async def on_ready(self):
        print('\nBot online')
        print(f'Name: {self.user.name}')
        print(f'ID: {self.user.id}')
        print('-' * (len(self.user.id) + len('ID: ')))

    async def confusion(self, message):
        """
        Adds a question mark emoji to a user's message to indicate something went wrong in some way.
        :param message: The offending message
        """
        if message is not None:
            question_emoji = '❓'  # The Unicode string of the question mark emoji - do not delete
            await self.add_reaction(message, question_emoji)

    async def on_message(self, message):
        await self.wait_until_ready()

        if message is None or message.author is None or message.author.bot is None \
                or not message.content.startswith(self.command_prefix):
            return

        normalized_message = message.content[len(self.command_prefix):].strip()

        matches = self._command_parser.parse_args(normalized_message)

        if matches is None or len(matches) <= 0:
            print(f"Command '{normalized_message}' does not match a command")
            await self.confusion(message)
            return

        for match in matches:
            try:
                command = match[0]  # command
                args = match[1]  # arguments to command from user
                await command.execute(CommandEvent(self, command, args, message))
            except CommandError as e:
                print(f"Error in running command '{command.aliases}': {e}")
                await self.confusion(message)

    def cleanup(self):
        # TODO MAKE SURE THIS WORKS
        if not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.logout(), self.loop)

    def _command_list(self):
        commands = []
        for plugin_name, plugin_instance in self._plugins.items():
            for command in plugin_instance.commands:
                commands.append(command)
        return commands

    def _listener_list(self):
        listeners = []
        for plugin_name, plugin_instance in self._plugins.items():
            for listener in plugin_instance.listeners:
                listeners.append(listener)
            return listeners

    def _load_plugins(self):
        plugins = {}

        # Generate portable pathway to plugins package
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        plugin_dir = os.path.join(plugin_dir, 'plugins')

        # Add plugin package to where the system looks for files.
        sys.path.append(plugin_dir)

        # Search each element within the plugins package.
        for package in os.listdir(plugin_dir):
            if package is None or package == 'example' or package == 'util':
                continue

            package_dir = os.path.join(plugin_dir, package)

            # Base module of plugin is 'name of package.py'
            if os.path.isdir(package_dir) and f'{package}.py' in os.listdir(package_dir):
                # Import the plugin's base module
                prog = importlib.import_module(f'dougbot.plugins.{package}.{package}')

                # Find all subclasses of Plugin
                for attribute_str in dir(prog):
                    attribute = getattr(prog, attribute_str)

                    if inspect.isclass(attribute) and issubclass(attribute, Plugin) and not attribute == Plugin:
                        plugin_instance = attribute()
                        plugin_name = plugin_instance.__class__.__name__
                        if plugin_name in plugins.keys():
                            raise Exception(f'Plugin {plugin_name} from {type(plugin_instance)} was already added or '
                                            f'shares name with {self._plugins[plugin_name]}')
                        plugins[plugin_instance.__class__.__name__] = plugin_instance

        sys.path.remove(plugin_dir)

        return plugins


if __name__ == '__main__':
    dougbot = DougBot('../../config/config.ini')
    dougbot.run()
