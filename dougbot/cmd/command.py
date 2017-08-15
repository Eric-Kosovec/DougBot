import abc

from discord.message import Message

from dougbot import *


class Command:
    __metaclass__ = abc.ABCMeta

    def __init__(self, title):
        self.title = title
        return

    @staticmethod
    @abc.abstractmethod
    async def run_command(bot: DougBot, message: Message, user_args, **kwargs):
        # For subclasses to implement.
        return
