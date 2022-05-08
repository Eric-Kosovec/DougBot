import asyncio
from logging import Formatter
from logging import Handler

from dougbot.common.logevent import LogEvent
from dougbot.common.messaging import message_utils


class ChannelHandler(Handler):
    _LOGGING_FORMAT = '%(levelname)s: %(message)s'

    def __init__(self, channel, loop):
        super().__init__()
        self._channel = channel
        self._loop = loop
        self.setFormatter(Formatter(self._LOGGING_FORMAT))

    def emit(self, record):
        send_failure = False
        send_failure_exception = None

        for message in message_utils.split_message(self.format(record)):
            if self._loop.is_closed():
                LogEvent('') \
                    .message(message) \
                    .fatal()
                continue

            try:
                asyncio.run_coroutine_threadsafe(self._channel.send(message), self._loop)
            except Exception as e:
                LogEvent('') \
                    .message(message) \
                    .fatal()
                send_failure = True
                send_failure_exception = e

        if send_failure:
            LogEvent(__file__) \
                .message('Failed to send error message to logging channel') \
                .exception(send_failure_exception) \
                .fatal()
