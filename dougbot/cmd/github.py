from discord.message import Message

import cmd.command
from dougbot import *


class GitHub(cmd.Command):
    def __init__(self):
        super().__init__(self.__class__.__name__)
        return

    @staticmethod
    async def run_command(bot: DougBot, message: Message):
        await bot.send_message(message.channel, bot.config.source_code)
