import asyncio
import importlib
import inspect
import os
import sys

import discord.client

from dougbot.config import Config
from dougbot.core.command import CommandEvent, CommandError
from dougbot.core.commandparser import CommandParser
from dougbot.core.listener import ListenerEvent, ListenerError
from dougbot.plugins.listento import ListenTo
from dougbot.plugins.plugin import Plugin
from dougbot.plugins.util.long_message import long_message


class DougBot(discord.Client):

    def __init__(self, config_file):
        super().__init__()
        self.config = Config(config_file)
        self.command_prefix = self.config.command_prefix

        self._method_to_listento = self._event_method_map()

        # TODO PROTECT SYSTEM DIRECTORIES FROM PLUGINS - CROSS-PLATFORM
        self._plugins = self._load_plugins()  # Dictionary of plugin name to Plugin class instance
        self._commands = self._command_list()
        self._event_listeners = self._listener_list()
        self._command_parser = CommandParser(self._commands)
        self._listento_to_listener = self._map_listeners(self._event_listeners)

    def _event_method_map(self):
        return {
            self.on_message: ListenTo.ON_MESSAGE,
            self.on_message_delete: ListenTo.ON_MESSAGE_DELETE,
            self.on_message_edit: ListenTo.ON_MESSAGE_EDIT,
            self.on_reaction_add: ListenTo.ON_REACTION_ADD,
            self.on_reaction_remove: ListenTo.ON_REACTION_REMOVE,
            self.on_reaction_clear: ListenTo.ON_REACTION_CLEAR,
            self.on_channel_delete: ListenTo.ON_CHANNEL_DELETE,
            self.on_channel_create: ListenTo.ON_CHANNEL_CREATE,
            self.on_channel_update: ListenTo.ON_CHANNEL_UPDATE,
            self.on_member_join: ListenTo.ON_MEMBER_JOIN,
            self.on_member_remove: ListenTo.ON_MEMBER_REMOVE,
            self.on_member_update: ListenTo.ON_MEMBER_UPDATE,
            self.on_server_join: ListenTo.ON_SERVER_JOIN,
            self.on_server_remove: ListenTo.ON_SERVER_REMOVE,
            self.on_server_update: ListenTo.ON_SERVER_UPDATE,
            self.on_server_role_create: ListenTo.ON_SERVER_ROLE_CREATE,
            self.on_server_role_delete: ListenTo.ON_SERVER_ROLE_DELETE,
            self.on_server_role_update: ListenTo.ON_SERVER_ROLE_UPDATE,
            self.on_server_emojis_update: ListenTo.ON_SERVER_EMOJIS_UPDATE,
            self.on_server_available: ListenTo.ON_SERVER_AVAILABLE,
            self.on_server_unavailable: ListenTo.ON_SERVER_UNAVAILABLE,
            self.on_voice_state_update: ListenTo.ON_VOICE_STATE_UPDATE,
            self.on_member_ban: ListenTo.ON_MEMBER_BAN,
            self.on_member_unban: ListenTo.ON_MEMBER_UNBAN,
            self.on_typing: ListenTo.ON_TYPING,
            self.on_group_join: ListenTo.ON_GROUP_JOIN,
            self.on_group_remove: ListenTo.ON_GROUP_REMOVE
        }

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

    async def send_message(self, destination, content=None, *, tts=False, embed=None):
        # TODO FIGURE OUT WHY I CAN'T PASS TTS AND EMBED
        for shorter_message in long_message(content):
            await super().send_message(destination, shorter_message)

    async def join_channel(self, channel):
        if channel is None or channel.is_private:
            return None

        vc = self.voice_client_in(channel.server)

        if vc is not None and vc.channel == channel:
            return vc
        elif vc is not None:
            await self.leave_channel(channel)

        # If there is a warning here, ignore it. Works perfectly fine
        return await self.join_voice_channel(channel)

    async def leave_channel(self, channel):
        if channel is None or channel.is_private:
            return

        vc = self.voice_client_in(channel.server)

        if vc is not None and vc.channel == channel:
            await vc.disconnect()

    async def on_message(self, message):
        await self.wait_until_ready()

        if message is None or message.author is None or message.author.bot is None:
            return

        await self._delegate_listener_call(self.on_message, message)

        if not message.content.startswith(self.command_prefix):
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

    @staticmethod
    def _map_listeners(listeners):
        listento_to_listeners = {}

        if listeners is not None:
            for listener in listeners:
                listento_to_listeners.setdefault(listener.args, []).append(listener)

        return listento_to_listeners

    def _listener_list(self):
        listener_list = []
        for plugin_name, plugin_instance in self._plugins.items():
            for listener in plugin_instance.event_listeners:
                listener_list.append(listener)
        return listener_list

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

    '''
    Start of code for listening for events for the Plugins.
    '''

    async def on_message_delete(self, message):
        await self._delegate_listener_call(self.on_message_delete, message)

    async def on_message_edit(self, before, after):
        await self._delegate_listener_call(self.on_message_edit, before, after)

    async def on_reaction_add(self, reaction, user):
        await self._delegate_listener_call(self.on_reaction_add, reaction, user)

    async def on_reaction_remove(self, reaction, user):
        await self._delegate_listener_call(self.on_reaction_remove, reaction, user)

    async def on_reaction_clear(self, message, reactions):
        await self._delegate_listener_call(self.on_reaction_clear, message, reactions)

    async def on_channel_delete(self, channel):
        await self._delegate_listener_call(self.on_channel_delete, channel)

    async def on_channel_create(self, channel):
        await self._delegate_listener_call(self.on_channel_create, channel)

    async def on_channel_update(self, before, after):
        await self._delegate_listener_call(self.on_channel_update, before, after)

    async def on_member_join(self, member):
        await self._delegate_listener_call(self.on_member_join, member)

    async def on_member_remove(self, member):
        await self._delegate_listener_call(self.on_member_remove, member)

    async def on_member_update(self, before, after):
        await self._delegate_listener_call(self.on_member_update, before, after)

    async def on_server_join(self, server):
        await self._delegate_listener_call(self.on_server_join, server)

    async def on_server_remove(self, server):
        await self._delegate_listener_call(self.on_server_remove, server)

    async def on_server_update(self, before, after):
        await self._delegate_listener_call(self.on_server_update, before, after)

    async def on_server_role_create(self, role):
        await self._delegate_listener_call(self.on_server_role_create, role)

    async def on_server_role_delete(self, role):
        await self._delegate_listener_call(self.on_server_role_delete, role)

    async def on_server_role_update(self, before, after):
        await self._delegate_listener_call(self.on_server_role_update, before, after)

    async def on_server_emojis_update(self, before, after):
        await self._delegate_listener_call(self.on_server_emojis_update, before, after)

    async def on_server_available(self, server):
        await self._delegate_listener_call(self.on_server_available, server)

    async def on_server_unavailable(self, server):
        await self._delegate_listener_call(self.on_server_unavailable, server)

    async def on_voice_state_update(self, before, after):
        await self._delegate_listener_call(self.on_voice_state_update, before, after)

    async def on_member_ban(self, member):
        await self._delegate_listener_call(self.on_member_ban, member)

    async def on_member_unban(self, server, user):
        await self._delegate_listener_call(self.on_member_unban, server, user)

    async def on_typing(self, channel, user, when):
        await self._delegate_listener_call(self.on_typing, channel, user, when)

    async def on_group_join(self, channel, user):
        await self._delegate_listener_call(self.on_group_join, channel, user)

    async def on_group_remove(self, channel, user):
        await self._delegate_listener_call(self.on_group_remove, channel, user)

    async def _delegate_listener_call(self, func, *args):
        try:
            # Function has no listeners associated with it
            if self._method_to_listento[func] not in self._listento_to_listener:
                return
            for listener in self._listento_to_listener[self._method_to_listento[func]]:
                if listener.listening:
                    await listener.execute(ListenerEvent(self, listener, args))
        except ListenerError as e:
            print(f"Error in listening to event '{func}': {e}")


if __name__ == '__main__':
    dougbot = DougBot('../../config/config.ini')
    dougbot.run()
