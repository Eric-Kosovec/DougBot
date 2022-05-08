import logging
import os
import sys
import traceback

from dougbot.config import RESOURCES_DIR


class LogEvent:
    _FATAL_LOG_FILE_MAX_BYTES = 5.12e+8  # 512 MB
    _FATAL_LOG_FILE_PATH = os.path.join(RESOURCES_DIR, 'fatal.log')

    def __init__(self, file):
        self._file = file
        self._class = ''
        self._message = ''
        self._exception = None
        self._objects = []

    def clazz(self, clazz):
        self._class = clazz.__qualname__
        return self

    def message(self, message):
        self._message += f"{' ' if len(self._message) else ''}{message}"
        return self

    def exception(self, exception):
        self._exception = exception
        return self

    def object(self, obj, message=''):
        self._objects.append((obj, message))
        return self

    def info(self, *, to_console=False):
        log_message = self._build_log_message()
        self.logger(self._file).info(log_message)

        if to_console:
            print(log_message, file=sys.stderr)

    def debug(self):
        log_message = self._build_log_message()
        print(log_message, file=sys.stderr)
        self.logger(self._file).debug(log_message)

    def warn(self, *, to_console=False):
        log_message = self._build_log_message()
        self.logger(self._file).warning(log_message)

        if to_console:
            print(log_message, file=sys.stderr)

    def error(self, *, to_console=False):
        log_message = self._build_log_message()
        self.logger(self._file).error(log_message)

        if to_console:
            print(log_message, file=sys.stderr)

    def fatal(self):
        """
        Print to stderr and log to file when bot instability won't allow logging to log channel
        """
        log_message = self._build_log_message()
        print(log_message, file=sys.stderr)

        try:
            if os.path.getsize(self._FATAL_LOG_FILE_PATH) >= self._FATAL_LOG_FILE_MAX_BYTES:
                os.remove(self._FATAL_LOG_FILE_PATH)
        except OSError as e:
            print(f'Failed to delete log file: {e}', file=sys.stderr)

        try:
            with open(self._FATAL_LOG_FILE_PATH, 'a') as fd:
                fd.write(log_message)
        except OSError as e:
            print(f'Failed to append to log file: {e}', file=sys.stderr)

    @staticmethod
    def logger(file=''):
        return logging.getLogger(file)

    @staticmethod
    def add_handler(handler, file=''):
        LogEvent.logger(file).addHandler(handler)

    @staticmethod
    def clear_handlers():
        LogEvent.logger('').handlers = []

    def _build_log_message(self):
        log_message = f"{self._file}{'' if self._class == '' else ' '}{self._class}: {self._message}\n"

        for obj, msg in self._objects:
            log_message += f'{msg}: {obj}\n'

        if self._exception is not None:
            log_message += f'{self._exception}\n{traceback.format_tb(self._exception.__traceback__)}\n'

        return log_message
