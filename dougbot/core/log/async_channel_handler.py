import asyncio
import os
import sys

import nextcord.utils
from aiologger.handlers.base import Handler
from aiologger.records import LogRecord

from dougbot import config
from dougbot.common.messaging import message_utils
from dougbot.config import RESOURCES_DIR


class AsyncChannelHandler(Handler):
    _DELIMITER = '-' * 100
    _FATAL_LOG_MAX_BYTES = config.get_configuration().fatal_log_size
    _FATAL_LOG_PATH = os.path.join(RESOURCES_DIR, 'fatal.log')

    def __init__(self, channel):
        super().__init__()

        if channel is not None:
            self._queue = asyncio.Queue()
            self._worker_task = asyncio.create_task(self._process_queue())

        self._channel = channel

    @property
    def initialized(self):
        return self._channel is not None

    async def emit(self, record: LogRecord) -> None:
        if not self.initialized:
            await self.handle_error(record)
            return

        try:
            await self._queue.put(record)
        except Exception as e:
            await self.handle_error(record, e)

    async def close(self) -> None:
        if not self.initialized:
            return

        try:
            await self._queue.join()

            self._worker_task.cancel()
            await self._worker_task
        except asyncio.CancelledError:
            pass

    async def handle_error(self, record: LogRecord, exception: Exception = None) -> None:
        try:
            normalized_record = await self._normalize_record(record)

            if exception:
                formatted_exception = self.formatter.format_traceback(exception.__traceback__)
                normalized_record = f'{normalized_record} meta_exception = {formatted_exception}'

            await asyncio.to_thread(self._append_fatal_log, normalized_record)
        except Exception as e:
            print(f'Failed to handle logging system error: {e}', file=sys.stderr)
            print(f'Was trying to log: {record}', file=sys.stderr)

    async def _process_queue(self):
        while True:
            record = await self._queue.get()
            if record is None:
                self._queue.task_done()
                continue

            try:
                await self._channel.send(self._DELIMITER)
            except Exception:
                pass

            try:
                normalized_record = await self._normalize_record(record)
                async for message in message_utils.async_split_message(normalized_record):
                    await self._channel.send(message)
            except Exception as e:
                await self.handle_error(record, e)
            finally:
                self._queue.task_done()


    async def _normalize_record(self, record: LogRecord):
        return nextcord.utils.escape_markdown(self.formatter.format(record))

    @staticmethod
    def _append_fatal_log(data):
        try:
            if os.path.getsize(AsyncChannelHandler._FATAL_LOG_PATH) >= AsyncChannelHandler._FATAL_LOG_MAX_BYTES:
                os.remove(AsyncChannelHandler._FATAL_LOG_PATH)
        except Exception as e:
            print(f'Failed to delete over-sized log file, appending anyway: {e}', file=sys.stderr)

        try:
            os.makedirs(os.path.dirname(AsyncChannelHandler._FATAL_LOG_PATH), exist_ok=True)
            with open(AsyncChannelHandler._FATAL_LOG_PATH, 'a') as fd:
                fd.write(data)
        except Exception as e:
            print(f'Failed to append to log file: {e}', file=sys.stderr)
            print(f'Failed to log data: {data}', file=sys.stderr)
