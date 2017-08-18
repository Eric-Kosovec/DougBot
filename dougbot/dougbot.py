import os
import sys

import discord.client
from discord import Message

from configdata import Config


class DougBot(discord.Client):
    _DEFAULT_CONFIG_FILE = "./config/config.ini"

    def __init__(self, config_file=_DEFAULT_CONFIG_FILE):
        self.config = Config(config_file)
        self.plugins = {}
        self._load_plugins()
        super().__init__()
        return

    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.config.token))
        except discord.errors.LoginFailure:
            print("Bot could not login. Bad token.")
        finally:
            # TODO CLEANUP
            self.loop.close()

    async def on_ready(self):
        # init_logger()

        print("Bot online")
        print("Name: %s" % self.user.name)
        print("ID: %s" % self.user.id)
        print("-----------------------")

    async def on_message(self, message: Message):
        # Wait until the bot is ready before checking messages.
        await self.wait_until_ready()

        # Avoid any sort of bot talking to bot type situation.
        if message.author.id == self.user.id or message.author.bot:
            return

        # Normalize message content
        norm_msg = message.content.lower()

        if not norm_msg.startswith(self.config.command_prefix):
            return

        (command, arguments) = self._parse_command(norm_msg, self.config.command_prefix)

        try:
            plugin = self.plugins[command]
        except KeyError as e:
            await self.send_message(message.channel, "%s is not a command." % command)
            return

        if plugin is None:
            await self.send_message(message.channel, "Command %s is not currently working." % command)
        else:
            try:
                await plugin.run(command, message, arguments, self)
            except Exception as e:
                await self.send_message(message.channel, "Command %s is not currently working." % command)
        return

    def _load_plugins(self):
        sys.path.append("plugins")

        for plugin in os.listdir("plugins"):
            if not plugin == "example.py" and plugin.endswith(".py"):
                plugin_name = plugin.split(".")[0].lower()
                prog = __import__(plugin_name)
                if hasattr(prog, "ALIASES") and len(prog.ALIASES) > 0:
                    for alias in prog.ALIASES:
                        self.plugins[alias.lower()] = prog
                else:
                    self.plugins[plugin_name] = prog

    @staticmethod
    def _parse_command(message: str, prefix: str):
        # Grab command and any arguments given

        first_space_idx = message.find(" ")

        if first_space_idx < 0:
            command = message[len(prefix):len(message)]
            arguments = ""
        else:
            command = message[len(prefix):first_space_idx]
            arguments = message[first_space_idx + 1:len(message)]

        return command, arguments


if __name__ == "__main__":
    dougbot = DougBot()
    dougbot.run()
