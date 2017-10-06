import asyncio
import importlib
import inspect
import os
import sys
import re

from threading import Thread

import discord.client

from dougbot.config import Config
from dougbot.plugins.plugin import Plugin
from dougbot.core.command import CommandEvent


# TODO LOGGING
# TODO FFMPEG TO PATH WITHOUT DOING IT MANUALLY


class DougBot(discord.Client):

    def __init__(self, config_file):
        super().__init__()
        self.config = Config(config_file)
        self._cmd_thread = None
        self._plugins = None

        self._load_plugins()
        self._commands_regex = self._create_commands_regex()
        self._commands_matcher = re.compile(self._commands_regex)

        # self.logger = get_logger()

    def run(self, *args, **kwargs):
        try:
            # Create thread to read console for exit command.
            self._cmd_thread = Thread(target=self._console_cmd_parse, daemon=True)
            self._cmd_thread.start()

            # Blocking function that does not return until the bot is done.
            super().run(*(self.config.token, *args), **kwargs)
        except Exception as e:
            print('Exception while running bot: %s' % e)
            self.cleanup()

    def _console_cmd_parse(self):
        bot_exit = False
        while not bot_exit:
            line = input()
            if line is not None and line.lower() == 'exit':
                bot_exit = True
        self.cleanup()
        sys.exit(0)

    '''
        Called when the bot is logged in and ready to take commands.
    '''
    async def on_ready(self):
        print('Bot online')
        print('Name: %s' % self.user.name)
        print('ID: %s' % self.user.id)
        print('-' * (len(self.user.id) + len('ID: ')))

    '''
        Called when a message is sent anywhere on the server, be it private message or channel message.
    '''
    async def on_message(self, message):
        if message is None:
            return

        # Wait until the bot is ready before checking messages.
        await self.wait_until_ready()

        # Avoid any sort of bot talking to bot-type situation.
        if message.author.id == self.user.id or message.author.bot:
            return

        if not message.content.startswith(self.config.command_prefix):
            return

        msg = message.content[len(self.config.command_prefix):]
        match = self._commands_matcher.fullmatch(msg)

        if match is None:
            print('NO MATCH')
            return

        commands_triggered = self._get_command_matches(msg)

        # Create a command event
        # command object created, message object, match object
        #event = CommandEvent()

        for command, match_obj in commands_triggered:
            event = CommandEvent(command, message, match_obj)

        #matched_commands = []
        print('IS A MATCH')
        #for command in self.commands:
        #    return

        # TODO Run the command

    def _get_command_matches(self, msg):
        commands = []

        for command in self.commands:
            match_obj = command.command_matcher.fullmatch(msg)
            if match_obj is not None:
                commands.append((command, match_obj))

        return commands

    @property
    def commands(self):
        for plugin, mdl in self._plugins.items():
            for command in mdl.get_commands():
                yield command

    def cleanup(self):
        if not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.logout(), self.loop)

    def _load_plugins(self):
        # Generate portable pathway to plugins
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        plugin_dir = os.path.join(plugin_dir, 'plugins')

        # Add plugin package to where the system looks for files.
        sys.path.append(plugin_dir)

        if self._plugins is None:
            self._plugins = {}

        # Search each element within the plugins folder.
        for package in os.listdir(plugin_dir):
            package_dir = os.path.join(plugin_dir, package)
            # Base module of plugin is 'name of package.py'
            if os.path.isdir(package_dir) and package + '.py' in os.listdir(package_dir):
                prog = importlib.import_module('dougbot.plugins.' + package + '.' + package)
                # Find all subclasses of Plugin
                for attr_str in dir(prog):
                    attr = getattr(prog, attr_str)
                    if inspect.isclass(attr) and issubclass(attr, Plugin) and not attr == Plugin:
                        plugin_instance = attr()
                        plugin_name = plugin_instance.__class__.__name__
                        if plugin_name in self._plugins.keys():
                            raise Exception('Plugin %s from %s was already added or shares names with %s'
                                            % (plugin_name, type(plugin_instance), self._plugins[plugin_name]))
                        self._plugins[plugin_instance.__class__.__name__] = plugin_instance

        sys.path.remove(plugin_dir)

    '''
        Accumulates all commands' regexes into one for command detection.
    '''
    def _create_commands_regex(self):
        commands_regex = ''

        spacer = ''
        for command in self.commands:
            commands_regex += spacer + command.get_regex()
            spacer = '|'

        return commands_regex


if __name__ == '__main__':
    dougbot = DougBot('../config/config.ini')
    dougbot.run()
