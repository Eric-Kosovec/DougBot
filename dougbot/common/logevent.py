import logging
import os
import sys
import traceback

from dateutil.tz import tz
from nextcord import Interaction
from nextcord.ext.commands import Context

from dougbot import config
from dougbot.config import CORE_DIR


# TODO MAKE ASYNCABLE WHEN NEEDED


class LogEvent:
    CHANNEL_FIELD = 'channel'
    CLASS_FIELD = 'class'
    CONTEXT_FIELD = 'context'
    LEVEL_FIELD = 'level'
    EXCEPTION_FIELD = 'exception'
    EXTENSION_FIELD = 'extension'
    INTERACTION_FIELD = 'interaction'
    MESSAGE_FIELD = 'message'
    METHOD_FIELD = 'method'
    MODULE_FIELD = 'module'

    _FATAL_LOG_MAX_BYTES = 5.12e+8  # 512 MB
    _FATAL_LOG_PATH = os.path.join(CORE_DIR, 'fatal.log')
    _ROOT_LOGGER_NAME = ''

    def __init__(self, module):
        if type(module) != str or len(module) == 0:
            raise ValueError('Invalid module name')

        self._fields = []
        self.add_field(self.MODULE_FIELD, module)

        self._log_to_console = config.get_configuration().log_to_console

    def channel(self, channel):
        return self.add_field(self.CHANNEL_FIELD, channel)

    def clazz(self, clazz):
        return self.add_field(self.CLASS_FIELD, clazz.__qualname__ if clazz else None)

    def context(self, ctx: Context):
        return self.add_field(self.CONTEXT_FIELD, ctx)

    def exception(self, exception):
        return self.add_field(self.EXCEPTION_FIELD, exception)

    def extension(self, extension):
        return self.add_field(self.EXTENSION_FIELD, extension)

    def interaction(self, interaction: Interaction):
        return self.add_field(self.INTERACTION_FIELD, interaction)

    def message(self, message):
        return self.add_field(self.MESSAGE_FIELD, message)

    def method(self, method):
        return self.add_field(self.METHOD_FIELD, method)

    def add_field(self, field, value):
        if type(field) != str or len(field) == 0:
            raise ValueError(f"Invalid field name '{field}'")

        if any(t for t in self._fields if t[0] == field):
            raise ValueError(f"Field '{field}' already exists")

        self._fields.append((field, value))
        return self

    def info(self, *, to_console=False):
        self.add_field(self.LEVEL_FIELD, 'INFO')

        log_message = self._build_output()
        self.logger(self._module_field()).info(log_message)

        if to_console or self._log_to_console:
            print(log_message, file=sys.stderr)

    def debug(self):
        self.add_field(self.LEVEL_FIELD, 'DEBUG')

        log_message = self._build_output()
        self.logger(self._module_field()).debug(log_message)

        print(log_message, file=sys.stderr)

    def warn(self, *, to_console=False):
        self.add_field(self.LEVEL_FIELD, 'WARN')

        log_message = self._build_output()
        self.logger(self._module_field()).warning(log_message)

        if to_console or self._log_to_console:
            print(log_message, file=sys.stderr)

    def error(self, *, to_console=False):
        self.add_field(self.LEVEL_FIELD, 'ERROR')

        log_message = self._build_output()
        self.logger(self._module_field()).error(log_message)

        if to_console or self._log_to_console:
            print(log_message, file=sys.stderr)

    def fatal(self):
        """
        Print to stderr and log to file when instability prevents logging to channel
        """
        self.add_field(self.LEVEL_FIELD, 'FATAL')

        log_message = self._build_output()
        print(log_message, file=sys.stderr)
        self._append_fatal_log(log_message)

    @staticmethod
    def logger(name=_ROOT_LOGGER_NAME):
        return logging.getLogger(name)

    @staticmethod
    def add_handler(handler, name=_ROOT_LOGGER_NAME):
        LogEvent.logger(name).addHandler(handler)

    @staticmethod
    def clear_handlers():
        LogEvent.logger(LogEvent._ROOT_LOGGER_NAME).handlers = []

    @staticmethod
    def log_fatal_file():
        log_data = LogEvent._read_fatal_log()
        if log_data:
            LogEvent.logger().error(f'Errors while bot was down:\n\n{log_data}\n\nEnd of offline errors')

    def _build_output(self):
        output = f'{self._fields[-1][0]} = {self._fields[-1][1]}\n'  # Error level field

        for field, value in self._fields[:-1]:
            output += f'{field} = '
            if field in [self.CONTEXT_FIELD, self.INTERACTION_FIELD]:
                output += f"'{value.message.clean_content}' from {value.message.author} at {self._time_as_cst(value.message.created_at)} CST"
            else:
                output += str(value)
                if field == self.EXCEPTION_FIELD:
                    output += f"\n{''.join(traceback.format_exception(value))}"
            output += '\n'

        return output

    def _module_field(self):
        return next(t[1] for t in self._fields if t[0] == self.MODULE_FIELD)

    @staticmethod
    def _time_as_cst(original_time):
        return original_time.astimezone(tz.gettz('America/Chicago'))

    @staticmethod
    def _read_fatal_log():
        log_data = None
        try:
            with open(LogEvent._FATAL_LOG_PATH) as fd:
                log_data = fd.read()
            os.remove(LogEvent._FATAL_LOG_PATH)
        except OSError:
            pass

        return log_data

    def _append_fatal_log(self, data):
        try:
            if os.path.getsize(self._FATAL_LOG_PATH) >= self._FATAL_LOG_MAX_BYTES:
                os.remove(self._FATAL_LOG_PATH)
        except OSError:
            pass

        try:
            os.makedirs(CORE_DIR, exist_ok=True)
            with open(self._FATAL_LOG_PATH, 'a') as fd:
                fd.write(data)
        except OSError as e:
            print(f'Failed to append to log file: {e}', file=sys.stderr)
