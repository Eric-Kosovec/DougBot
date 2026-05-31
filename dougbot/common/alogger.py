import asyncio
import os
import sys
import traceback
from datetime import time

from aiologger import Logger
from nextcord import Interaction
from nextcord.ext.commands import Context
from nextcord.utils import format_dt

from dougbot import config
from dougbot.config import RESOURCES_DIR


class AsyncLogger:
    _FATAL_LOG_PATH = os.path.join(RESOURCES_DIR, 'fatal.log')
    _LOG_DEBUG = lambda m: AsyncLogger._LOGGER.debug(m)
    _LOG_ERROR = lambda m: AsyncLogger._LOGGER.error(m)
    _LOG_FATAL = lambda m: AsyncLogger._LOGGER.fatal(m)
    _LOG_INFO = lambda m: AsyncLogger._LOGGER.info(m)
    _LOG_QUEUE = asyncio.PriorityQueue()
    _LOG_WARN = lambda m: AsyncLogger._LOGGER.warning(m)
    _LOGGER = Logger(name='DougBot')
    _PROCESSING_TASK = None

    # TODO NEED TO CALL WHEN LOOP GETS ESTABLISHED
    @classmethod
    async def start(cls):
        if cls._PROCESSING_TASK is None:
             cls._PROCESSING_TASK = asyncio.create_task(cls._process_log_queue())

    @classmethod
    async def close(cls):
        await cls._LOG_QUEUE.join()

        if cls._PROCESSING_TASK:
            cls._PROCESSING_TASK.cancel()

            try:
                await cls._PROCESSING_TASK
            except asyncio.CancelledError:
                pass

            cls._PROCESSING_TASK = None

        await cls._LOGGER.shutdown()

    @classmethod
    async def info(cls, module, *, message=None, exception=None, to_console=False, **kwargs):
        asyncio.create_task(cls._enqueue_log(cls._LOG_INFO, time(), module, message, exception, to_console, **kwargs))

    @classmethod
    async def debug(cls, module, *, message=None, exception=None, to_console=True, **kwargs):
        asyncio.create_task(cls._enqueue_log(cls._LOG_DEBUG, time(), module, message, exception, to_console, **kwargs))

    @classmethod
    async def warn(cls, module, *, message=None, exception=None, to_console=False, **kwargs):
        asyncio.create_task(cls._enqueue_log(cls._LOG_WARN, time(), module, message, exception, to_console, **kwargs))

    @classmethod
    async def error(cls, module, *, message=None, exception=None, to_console=False, **kwargs):
        asyncio.create_task(cls._enqueue_log(cls._LOG_ERROR, time(), module, message, exception, to_console, **kwargs))

    @classmethod
    async def fatal(cls, module, *, message=None, exception=None, to_console=True, **kwargs):
        """
        Print to stderr and log to file when instability prevents logging to channel
        """
        asyncio.create_task(cls._enqueue_log(cls._LOG_FATAL, time(), module, message, exception, to_console, **kwargs))

    @classmethod
    async def log_pending(cls):
        async def log():
            fatal_log = await asyncio.to_thread(cls._read_fatal_log)
            if fatal_log:
                await cls._LOGGER.error(f'Errors while bot was down:\n\n{fatal_log}\n\nEnd of offline errors')

        asyncio.create_task(log())

    @classmethod
    async def set_handler(cls, handler):
        handlers = cls._LOGGER.handlers

        if not handler:
            return

        if len(handlers) == 1:
            asyncio.create_task(handlers[0].close())
            handlers.clear()

        cls._LOGGER.add_handler(handler)

    @classmethod
    async def _process_log_queue(cls):
        while True:
            # TODO DO I NEED TIMESTAMP OR DOES THE LOG SYSTEM DO IT?
            log_func, timestamp, module, message, exception, to_console, kwargs = await cls._LOG_QUEUE.get()
            try:
                log_output = await cls._build_output(module, message, exception, **kwargs)
                await log_func(log_output)

                if to_console or config.get_configuration().log_to_console:
                    await asyncio.to_thread(lambda: print(log_output, file=sys.stderr))
            except Exception as e:
                print(f'Failed to process log: {e}\nLog message was: {message}', file=sys.stderr)
            finally:
                cls._LOG_QUEUE.task_done()

    @classmethod
    async def _enqueue_log(cls, log_func, timestamp, module, message=None, exception=None, to_console=False, **kwargs):
        await cls._LOG_QUEUE.put((log_func, timestamp, module, message, exception, to_console, kwargs))

    @staticmethod
    async def _build_output(module, message=None, exception=None, **kwargs):
        output = [f'{module = }']

        if message:
            output.append(f'{message = }')

        for field, value in kwargs.items():
            output.append(f'{field} = {AsyncLogger._format_value(value)}')

        if exception:
            output.append(f"{exception}\n{''.join(traceback.format_exception(exception))}")

        return '\n'.join(output)

    @staticmethod
    async def _format_value(value):
        if isinstance(value, (Context, Interaction)):
            return (
                f"'{value.message.clean_content}' from "
                f"{value.message.author} at {format_dt(value.message.created_at)}"
            )
        elif isinstance(value, Exception):
            return f"{value}\n{''.join(traceback.format_exception(value))}"

        return str(value)

    @classmethod
    def _read_fatal_log(cls):
        try:
            if not os.path.exists(cls._FATAL_LOG_PATH):
                return None

            with open(cls._FATAL_LOG_PATH) as fd:
                fatal_log = fd.read()

            os.remove(cls._FATAL_LOG_PATH)

            return fatal_log
        except Exception as e:
            print(f'Failed to read fatal log file: {e}', file=sys.stderr)
            return None
