import asyncio
import logging
import os
import sys
import traceback
from enum import Enum

from nextcord import Interaction
from nextcord.ext.commands import Context
from nextcord.utils import format_dt

from dougbot import config
from dougbot.config import RESOURCES_DIR


class AsyncLogger:
    _FATAL_LOG_MAX_BYTES = config.get_configuration().fatal_log_size
    _FATAL_LOG_PATH = os.path.join(RESOURCES_DIR, 'fatal.log')
    _ROOT_LOGGER_NAME = ''

    @staticmethod
    async def info(module, *, message=None, exception=None, to_console=False, **kwargs):
        await asyncio.to_thread(AsyncLogger._log, _LogLevel.INFO, module, message, exception, to_console,
                                **kwargs)

    @staticmethod
    async def debug(module, *, message=None, exception=None, to_console=True, **kwargs):
        await asyncio.to_thread(AsyncLogger._log, _LogLevel.DEBUG, module, message, exception, to_console,
                                **kwargs)

    @staticmethod
    async def warn(module, *, message=None, exception=None, to_console=False, **kwargs):
        await asyncio.to_thread(AsyncLogger._log, _LogLevel.WARN, module, message, exception, to_console,
                                **kwargs)

    @staticmethod
    async def error(module, *, message=None, exception=None, to_console=False, **kwargs):
        await asyncio.to_thread(AsyncLogger._log, _LogLevel.ERROR, module, message, exception, to_console,
                                **kwargs)

    @staticmethod
    async def fatal(module, *, message=None, exception=None, to_console=True, **kwargs):
        """
        Print to stderr and log to file when instability prevents logging to channel
        """
        await asyncio.to_thread(AsyncLogger._log, _LogLevel.FATAL, module, message, exception, to_console,
                                **kwargs)

    @staticmethod
    async def add_handler(handler, name=_ROOT_LOGGER_NAME):
        # addHandler acquires a lock
        await asyncio.to_thread(logging.getLogger(name).addHandler, handler)

    @staticmethod
    async def log_fatal_file():
        await asyncio.to_thread(AsyncLogger._log_fatal_file)

    @staticmethod
    async def read_fatal_log():
        await asyncio.to_thread(AsyncLogger._read_fatal_log)

    @staticmethod
    def _log(level, module, message=None, exception=None, to_console=False, **kwargs):
        log_message = AsyncLogger._build_output(module, level, message, exception, **kwargs)

        logger_name = 'Unknown' if module is None else module
        logger = None if level == _LogLevel.FATAL else logging.getLogger(logger_name)

        if level == _LogLevel.DEBUG:
            logger.debug(log_message)
        elif level == _LogLevel.INFO:
            logger.info(log_message)
        elif level == _LogLevel.FATAL:
            AsyncLogger._append_fatal_log(log_message)
        elif level == _LogLevel.WARN:
            logger.warning(log_message)
        else:
            logger.error(log_message)

        if to_console or config.get_configuration().log_to_console:
            print(log_message, file=sys.stderr)

    @staticmethod
    def _build_output(level, module, message=None, exception=None, **kwargs):
        output = f'{level = }\n{module = }\n'

        if message is not None:
            output += f'{message = }\n'

        for field, value in kwargs:
            output += f'{field} = '

            if type(value) in [Context, Interaction]:
                output += f"'{value.message.clean_content}' from " \
                          f"{value.message.author} at {format_dt(value.message.created_at)}"
            elif isinstance(value, Exception):
                output += f"{value}\n{''.join(traceback.format_exception(value))}"
            else:
                output += f'{value}'

            output += '\n'

        if exception is not None:
            output += f"{exception}\n{''.join(traceback.format_exception(exception))}"

        return output

    @staticmethod
    def _log_fatal_file():
        fatal_log = AsyncLogger._read_fatal_log()
        if fatal_log:
            logging.getLogger(AsyncLogger._ROOT_LOGGER_NAME) \
                .error(f'Errors while bot was down:\n\n{fatal_log}\n\nEnd of offline errors')

    @staticmethod
    def _read_fatal_log():
        fatal_log = None

        try:
            if not os.path.exists(AsyncLogger._FATAL_LOG_PATH):
                return None

            with open(AsyncLogger._FATAL_LOG_PATH) as fd:
                fatal_log = fd.read()

            os.remove(AsyncLogger._FATAL_LOG_PATH)
        except OSError as e:
            print(f'Failed to read fatal log file: {e}', file=sys.stderr)

        return fatal_log

    @staticmethod
    def _append_fatal_log(data):
        try:
            if os.path.getsize(AsyncLogger._FATAL_LOG_PATH) >= AsyncLogger._FATAL_LOG_MAX_BYTES:
                os.remove(AsyncLogger._FATAL_LOG_PATH)
        except OSError as e:
            print(f'Failed to delete over-sized log file, appending anyway: {e}', file=sys.stderr)

        try:
            os.makedirs(os.path.dirname(AsyncLogger._FATAL_LOG_PATH), exist_ok=True)
            with open(AsyncLogger._FATAL_LOG_PATH, 'a') as fd:
                fd.write(data)
        except OSError as e:
            print(f'Failed to append to log file: {e}', file=sys.stderr)


class _LogLevel(Enum):
    DEBUG = 0
    ERROR = 1
    FATAL = 2
    INFO = 3
    WARN = 4
