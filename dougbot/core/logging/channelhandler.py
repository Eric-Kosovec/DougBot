import asyncio
import logging
from logging import Handler
from pprint import pprint

from dougbot.common.long_message import long_message


class ChannelHandler(Handler):

    def __init__(self, channel, loop):
        super().__init__()
        self._channel = channel
        self._loop = loop
        self.setFormatter(logging.Formatter('{%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'))

    def emit(self, record):
        for message in long_message(self.format(record)):
            if not self._loop.is_closed():
                asyncio.run_coroutine_threadsafe(self._channel.send(message), self._loop)
            else:
                pprint(message)
