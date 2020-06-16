import asyncio
import logging
import os
from logging import Handler

from dougbot.extensions.util.long_message import long_message


class ChannelHandler(Handler):
    _FORMATTER = logging.Formatter('{%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

    def __init__(self, root_dir, channel, loop):
        super().__init__()
        if root_dir is None or channel is None or loop is None:
            raise ValueError('ChannelHandler init given None value')
        self._root_dir = root_dir
        self._channel = channel
        self._loop = loop
        self.setFormatter(self._FORMATTER)

    def emit(self, record):
        # Eliminates logging from exceptions caused by library code.
        if os.path.splitdrive(record.pathname)[0] != os.path.splitdrive(self._root_dir)[0] or \
                os.path.commonpath([record.pathname, self._root_dir]) != self._root_dir:
            return
        record_text = self.format(record)
        for message in long_message(record_text):
            asyncio.run_coroutine_threadsafe(self._channel.send(message), self._loop)
