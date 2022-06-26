import asyncio
import os
from logging import Formatter
from logging import Handler

from dougbot.common.logevent import LogEvent
from dougbot.common.messaging import message_utils


class ChannelHandler(Handler):
    _LOGGING_FORMAT = '%(message)s'

    def __init__(self, root_dir, channel, loop):
        super().__init__()
        self._root_dir = root_dir
        self._channel = channel
        self._loop = loop
        self.setFormatter(Formatter(self._LOGGING_FORMAT))

    def emit(self, record):
        if self._from_library(record):
            return

        for message in message_utils.split_message(self.format(record)):
            try:
                asyncio.run_coroutine_threadsafe(self._channel.send(message), self._loop)
            except Exception as e:
                self.handleError(record, e)
                return
        asyncio.run_coroutine_threadsafe(self._channel.send('---------------'), self._loop)

    def handleError(self, record, exception=None):
        LogEvent(__file__) \
            .message('ChannelHandler failed to send log') \
            .add_field('record', self.format(record)) \
            .exception(exception) \
            .fatal()

    def _from_library(self, record):
        return os.path.splitdrive(record.pathname)[0] != os.path.splitdrive(self._root_dir)[0] or \
               os.path.commonpath([record.pathname, self._root_dir]) != self._root_dir
