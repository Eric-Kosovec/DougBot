import inspect
from enum import Enum

from dougbot.core.command import Command, CommandSpecError
from dougbot.core.listener import Listener, ListenerSpecError

_PLUGIN_ELEMENT_ATTR = '_dougbot_plugin_element'


class PluginError(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class _PluginElementType(Enum):
    COMMAND = 'command'
    LISTENER = 'listener'


class _PluginDecor:

    # cls is class of plugin
    # args is tuple
    # kwargs is dict
    @classmethod
    def command(cls, *args, **kwargs):
        def wrapper(func):
            cls._append_element(func, _PluginElementType.COMMAND, *args, **kwargs)
            return func

        return wrapper

    @classmethod
    def listen(cls, *args, **kwargs):
        def wrapper(func):
            cls._append_element(func, _PluginElementType.LISTENER, *args, **kwargs)
            return func

        return wrapper

    @classmethod
    def _append_element(cls, func, element_type, *args, **kwargs):
        if cls is None or func is None or element_type is None or args is None or kwargs is None:
            return

        if not hasattr(func, _PLUGIN_ELEMENT_ATTR):
            func._dougbot_plugin_element = []

        func._dougbot_plugin_element.append({
            'type': element_type,
            'args': args,
            'kwargs': kwargs
        })


class Plugin(_PluginDecor):

    def __init__(self):
        super().__init__()

        self._commands = []
        self._event_listeners = []

        # Goes through each method of the Plugin class and all subclasses
        # in form (name, function)
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(func, _PLUGIN_ELEMENT_ATTR):
                for element in getattr(func, _PLUGIN_ELEMENT_ATTR):
                    self._delegate_element(element, func)
                # TODO CLEANUP THE ATTRIBUTE WE CREATED; NOT A BIG DEAL, BUT CLEANER THAT WAY

    @property
    def commands(self):
        for command in self._commands:
            yield command

    @property
    def event_listeners(self):
        return self._event_listeners

    def _delegate_element(self, element, func):
        if element['type'] == _PluginElementType.COMMAND:
            self._add_command(func, *element['args'], **element['kwargs'])
        elif element['type'] == _PluginElementType.LISTENER:
            self._add_listener(func, *element['args'], **element['kwargs'])

    def _add_command(self, func, *args, **kwargs):
        try:
            self._commands.append(Command(self, func, *args, **kwargs))
        except CommandSpecError as e:
            print(f"Error in command '{func}' specification: {e}")

    def _add_listener(self, func, *args, **kwargs):
        try:
            self._event_listeners.append(Listener(self, func, *args, **kwargs))
        except ListenerSpecError as e:
            print(f"Error in listener '{func}' specification: {e}")
