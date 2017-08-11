import discord.client
from discord.message import Message

from DougBotProperties import *


class DougBot(discord.Client):
    # TODO FINISH THIS CLASS AND MAKE THE COMMANDS IN A MODULAR FASHION:
    # THAT IS, REGISTER THE COMMANDS WITH DOUGBOT FROM ONE PLACE?
    def __init__(self):
        self.voice = None

        super().__init__()
        return

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
        norm_msg = message.content.strip().casefold()

        if not self._is_command(norm_msg, COMMAND_PREFIX):
            return

        (command, arguments) = self._parse_command(norm_msg, COMMAND_PREFIX)

        # Call proper command with arguments, if need be.
        if not hasattr(self, "cmd_%s" % command):
            print("There is no command %s" % command)
            return

        # Gets the function having the prefix cmd_ within the DougBot class.
        func = getattr(self, "cmd_%s" % command)

        # TODO FIGURE OUT HOW TO PASS ARGUMENTS TO FUNCTIONS WITH VARYING REQUIREMENTS
        # ALSO, FIGURE OUT HOW TO MAKE COMMANDS INTO MODULES, WHEREBY THEY LIE IN A SEPARATE FILE
        # AND CAN BE HOOKED INTO DOUGBOT
        await func(message)

        return

    async def cmd_ping(self, message: Message):
        await self.send_message(message.channel, "Pong")

    async def cmd_github(self, message: Message):
        await self.send_message(message.channel, GITHUB)

    async def cmd_join(self, message: Message):
        # Don't join a channel if this was a private message
        if message.channel.is_private:
            return

        # Get the voice channel the user is in and join that one.
        voice_channel = message.author.voice.voice_channel

        # User is not in a voice channel, ignore them.
        if voice_channel is None:
            print("USER NOT IN VOICE CHANNEL")
            return

        # TODO Check if we are already in the channel

        await self.join_voice_channel(voice_channel)

    async def cmd_leave(self, message: Message):
        # Don't leave channel if this was a private message
        if message.channel.is_private:
            return

        # Message is not from a user within a voice channel.
        if message.author.voice.voice_channel is None:
            return

        print("Author's channel: ")
        print(message.author.voice.voice_channel)

        # Get the VoiceClient object of the bot's from the server the message was sent from.
        bot_voice_client = self.voice_client_in(message.server)

        print("Out voiceclient is ")
        print(self.voice)
        print()

        # TODO: BOT NEVER HAS A LEGIT VOICECLIENT OBJECT, APPARENTLY

        # Bot is not in a voice channel on the server.
        if bot_voice_client is None:
            print("NOT IN VOICE CHANNEL ON SERVER")
            return

        await bot_voice_client.disconnect()

    @staticmethod
    def _is_command(message: str, prefix: str):
        return message.startswith(prefix)

    @staticmethod
    def _parse_command(message: str, prefix: str):
        # Grab command and any arguments given

        first_space_idx = message.find(" ")

        if first_space_idx < 0:
            command = message[len(prefix):len(message)]
            arguments = ""
        else:
            command = message[len(prefix):first_space_idx]
            arguments = message[first_space_idx + 1:len(message)].strip()

        return command, arguments


if __name__ == "__main__":
    dougbot = DougBot()
    dougbot.run(TOKEN)
