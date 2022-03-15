import logging
import os
import sys
import traceback

from dougbot.config import RESOURCES_DIR


class LogEvent:
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
        self._message = message
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
        log_message = self._build_log_message()
        print(log_message, file=sys.stderr)

        with open(self._FATAL_LOG_FILE_PATH, 'w') as fd:
            fd.write(log_message)

        self.logger(self._file).critical(log_message)

    @staticmethod
    def logger(file):
        return logging.getLogger(file)

    @staticmethod
    def add_handler(handler):
        """
        For Core use only
        :param handler: handler for log
        """
        LogEvent.logger('').addHandler(handler)

    def _build_log_message(self):
        log_message = f"{self._file}{'' if self._class == '' else ' '}{self._class}: {self._message}\n"

        for obj, msg in self._objects:
            log_message += f'{msg}: {obj}\n'

        if self._exception is not None:
            log_message += f'{self._exception}\n{traceback.format_tb(self._exception.__traceback__)}\n'

        return log_message
