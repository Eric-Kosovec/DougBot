import asyncio
from logging import Formatter
from logging import Handler

from dougbot.common.logger import Logger
from dougbot.common.messaging import message_utils


class ChannelHandler(Handler):
    _LOGGING_FORMAT = '%(message)s'
    _MARKDOWN_CHARACTERS = '*_~|>`'
    _LOG_DELIMITER = '-' * 100

    def __init__(self, root_dir, channel, loop):
        super().__init__()
        self._root_dir = root_dir
        self._channel = channel
        self._loop = loop
        self.setFormatter(Formatter(self._LOGGING_FORMAT))

    def emit(self, record):
        if self._from_library(record):
            return

        self._run_coroutine(self._channel.send(self._LOG_DELIMITER))

        # TODO THREADED ASYNC LOGGING SYSTEM
        # TODO SMART SPLIT ON FIELDS AND REMOVE EMBEDS
        for message in message_utils.split_message(self._normalize_record(record)):
            try:
                self._run_coroutine(self._channel.send(message))
            except Exception as e:
                self.handleError(record, e)
                return

    def handleError(self, record, exception=None):
        Logger(__file__) \
            .message('ChannelHandler failed to send log') \
            .add_field('record', self.format(record)) \
            .exception(exception) \
            .fatal()

    def _normalize_record(self, record):
        return self._escape_markdown(self.format(record))

    def _escape_markdown(self, text):
        escaped_text = text
        for c in self._MARKDOWN_CHARACTERS:
            escaped_text = escaped_text.replace(c, '\\' + c)
        return escaped_text

    def _run_coroutine(self, coroutine):
        asyncio.run_coroutine_threadsafe(coroutine, self._loop)

    def _from_library(self, record):
        return False
