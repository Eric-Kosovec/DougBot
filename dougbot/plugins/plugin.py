import inspect

from dougbot.core.command import Command

_PLUGIN_ELEMENT_VAR = '_dougbot_plugin_element'


class PluginDecor:
    # cls is class of plugin
    # args is tuple
    # kwargs is dict
    @classmethod
    def command(cls, *args, **kwargs):
        def wrapper(func):
            cls._append_element(func, 'command', *args, **kwargs)
            return func

        return wrapper

    @classmethod
    def listen(cls, *args, **kwargs):
        def wrapper(func):
            cls._append_element(func, 'listen', *args, **kwargs)
            return func

        return wrapper

    @classmethod
    def _append_element(cls, func, element_type, *args, **kwargs):
        if not hasattr(func, _PLUGIN_ELEMENT_VAR):
            func._dougbot_plugin_element = []

        func._dougbot_plugin_element.append({
            'type': element_type,
            'args': args,
            'kwargs': kwargs
        })


class Plugin(PluginDecor):
    def __init__(self):
        super().__init__()

        self.bot = None
        self._commands = []
        self.listeners = []

        # Goes through each method of the Plugin class and all subclasses
        # in form (name, function)
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(func, _PLUGIN_ELEMENT_VAR):
                for element in getattr(func, _PLUGIN_ELEMENT_VAR):
                    self._delegate_element(element, func)

    def get_commands(self):
        for command in self._commands:
            yield command

    def _delegate_element(self, element, func):
        if element['type'] == 'command':
            self._add_command(func, *element['args'], **element['kwargs'])
        elif element['type'] == 'listen':
            self._add_listener(func, *element['args'], **element['kwargs'])

    def _add_listener(self, *args, **kwargs):
        print("Adding listener: %s" % args[0])
        return

    def _add_command(self, func, *args, **kwargs):
        self._commands.append(Command(self, func, *args, **kwargs))
