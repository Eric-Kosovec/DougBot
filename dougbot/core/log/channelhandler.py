import asyncio
import sys
from logging import Formatter
from logging import Handler

from dougbot.common.messaging import message_utils


class ChannelHandler(Handler):
    _LOGGING_FORMAT = '%(levelname)s: %(message)s'

    def __init__(self, channel, loop):
        super().__init__()
        self._channel = channel
        self._loop = loop
        self.setFormatter(Formatter(self._LOGGING_FORMAT))

    def emit(self, record):
        for message in message_utils.split_message(self.format(record)):
            if self._loop.is_closed():
                print(message, sys.stderr)
            else:
                asyncio.run_coroutine_threadsafe(self._channel.send(message), self._loop).result()
