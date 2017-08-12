import discord.client
from discord.message import Message

from Config import *


class DougBot(discord.Client):
    # TODO BREAKS IF BOT IS STARTED FROM RUN.PY
    _DEFAULT_CONFIG_FILE = "../config/config.ini"

    # TODO FINISH THIS CLASS AND MAKE THE COMMANDS IN A MODULAR FASHION:
    # THAT IS, REGISTER THE COMMANDS WITH DOUGBOT FROM ONE PLACE?
    def __init__(self, config_file=_DEFAULT_CONFIG_FILE):
        self.config = Config(config_file)
        # Soundplayer dictionary in form server:soundplayer
        self.sound_players = dict()
        super().__init__()
        return

    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.config.token))
        except discord.errors.LoginFailure:
            print("Bot could not login. Bad token.")
        finally:
            # TODO FIX CLEANUP
            for vc in self.voice_clients:
                vc.disconnect()
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
        norm_msg = message.content.strip().casefold()

        ## TODO MAYBE INSTEAD DO SOMETHING LIKE STARTSWITH(PREFIX + COMMAND)

        if not self._is_command_form(norm_msg, self.config.command_prefix):
            return

        (command, arguments) = self._parse_command(norm_msg, self.config.command_prefix)

        # Call proper command with arguments, if need be.
        if not hasattr(self, "cmd_%s" % command):
            print("There is no command %s" % command)
            return

        # Gets the function having the prefix cmd_ within the DougBot class.
        func = getattr(self, "cmd_%s" % command)

        # !!!! TODO FIGURE OUT HOW TO PASS ARGUMENTS TO FUNCTIONS WITH VARYING REQUIREMENTS
        # ALSO, FIGURE OUT HOW TO MAKE COMMANDS INTO MODULES, WHEREBY THEY LIE IN A SEPARATE FILE
        # AND CAN BE HOOKED INTO DOUGBOT
        await func(message)

        return

    async def cmd_ping(self, message: Message):
        await self.send_message(message.channel, "Pong")

    async def cmd_github(self, message: Message):
        await self.send_message(message.channel, self.config.source_code)

    async def cmd_join(self, message: Message):
        # Don't join a channel if this was a private message, unless it's from the owner.
        if message.channel.is_private:
            return

        # Get the voice channel the user is in and join that one.
        user_voice_channel = message.author.voice.voice_channel

        # User is not in a voice channel, ignore them.
        if user_voice_channel is None:
            return

        # Check if we are already in a channel on the server
        if self.voice_client_in(message.server) is not None:
            return

        # Check if we are already in the channel
        for vc in self.voice_clients:
            if vc.channel == user_voice_channel:
                return

        await self.join_voice_channel(user_voice_channel)

    async def cmd_leave(self, message: Message):
        # Don't leave channel if this was a private message, unless it's from the owner.
        if message.channel.is_private:
            return

        # Message is not from a user within a voice channel.
        if message.author.voice.voice_channel is None:
            return

        # Get the VoiceClient object of the bot's from the server the message was sent from.
        bot_voice_client = self.voice_client_in(message.server)

        # Bot is not in a voice channel on the server.
        if bot_voice_client is None:
            return

        await bot_voice_client.disconnect()

    # NOTE: ALL TAKES PLACE WITHIN SERVER'S RESPECTIVE SOUNDPLAYER
    # PLAY WILL START PLAYING FROM THE QUEUE - DON'T PLAY IF ALREADY PLAYING
    # QUEUE WILL ADD TO QUEUE (WITH START/END TIMESTAMP)
    # STOP WILL END THE CURRENTLY PLAYING AUDIO (SOFT STOP, IDEALLY)
    # NEXT WILL PLAY NEXT IN QUEUE
    # CLEAR QUEUE WILL REMOVE ALL SONGS
    # REMOVE LINK WILL REMOVE THE GIVEN LINK FROM QUEUE
    # REMOVE BY ITSELF WILL REMOVE CURRENT PLAYING OR FRONT OF QUEUE ITEM
    # VOLUME # CHANGES VOLUME
    # CURR VOLUME DISPLAY VOLUME
    # FFW
    # SKIP ONTO NEXT TRACK
    # LEAVE WILL MAKE IT STOP TRACK, CLEAR QUEUE, LEAVE
    # JOIN PLAYS CURRENT QUEUE
    # NOW PLAYING
    # DEQUEUE # ?

    async def cmd_play(self, message: Message):
        print("IN PLAY")

        await self.cmd_join(message)
        player = await self.voice_client_in(message.server).create_ytdl_player(
            'https://www.youtube.com/watch?v=utH9UCr0p8Q')
        player.start()

        return

    @staticmethod
    def _is_command_form(message: str, prefix: str):
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
    dougbot.run()
