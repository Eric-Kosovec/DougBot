import inspect
from enum import Enum

from dougbot.core import argument
from dougbot.core.argument import Argument


class CommandLevel(Enum):
    OWNER = 5
    BLOCKED = 4
    ADMIN = 3
    USER = 2
    NULL = 1


class CommandError(Exception):

    def __init__(self, msg):
        self.msg = msg


class CommandSpecError(CommandError):

    def __init__(self, msg):
        super().__init__(msg)


class Command:

    def __init__(self, plugin, func, *args, **kwargs):
        self.plugin = plugin
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.aliases, arg_start = self._parse_aliases(*args)

        if len(self.aliases) <= 0:
            raise CommandSpecError('Command requires at least one alias')

        self.arguments = self._parse_arguments(arg_start, self._get_optional_list(self.func), *args)

    async def execute(self, event):
        try:
            await self.func(event, *event.args)
        except Exception as e:
            raise CommandError(e)

    @staticmethod
    def _get_optional_list(func):
        optional_list = []

        skip = True

        function_sig = inspect.signature(func)

        for parameter in function_sig.parameters:
            if skip:  # Skip over first parameter, which is a place for the CommandEvent object
                skip = False
                continue
            optional_list.append(function_sig.parameters[parameter].default != inspect.Parameter.empty)

        return optional_list

    @staticmethod
    def _parse_arguments(args_start, arg_optional, *args):
        if args_start is None or arg_optional is None or args is None:
            raise CommandError('Parse arguments was given None')
        if args_start < 0:
            raise CommandError('Argument start was negative')

        if args_start >= len(args):  # There were only aliases
            return []
        if len(args) - args_start > len(arg_optional):
            raise CommandSpecError('More types than parameters')
        elif len(args) - args_start < len(arg_optional):
            raise CommandSpecError('More parameters than types')

        argument_list = []

        for i in range(args_start, len(args)):
            try:
                argument_list.append(Argument(args[i], arg_optional[i - args_start]))
            except TypeError as e:
                raise CommandError(f'Invalid argument specification for command: {e}')

        saw_optional_arg = False
        saw_string = False
        # Check the arguments are well-formed to specification
        for i in range(len(argument_list)):
            # Make sure optional arguments follow non-optional arguments
            if argument_list[i].optional:
                saw_optional_arg = True
            elif saw_optional_arg:
                raise CommandSpecError('Non-optional argument follows optional argument')

            # Make sure strings are at the end and only one of them
            if argument_list[i].arg_type == str and saw_string:
                raise CommandSpecError('Only one string allowed. Must do your own parsing of the string.')
            elif argument_list[i].arg_type == str:
                saw_string = True
            if saw_string and argument_list[i].arg_type != str:
                raise CommandSpecError('String can only be at the end of the specification')

        return argument_list

    @staticmethod
    def _parse_aliases(*args):
        if args is None:
            raise CommandError("Command's argument list is None")

        given_alias_list = False  # Indicate if the aliases are within a list
        given_aliases = args

        if len(args) > 0 and type(args[0]) == list:
            given_aliases = args[0]
            given_alias_list = True

        alias_list = []

        for alias in given_aliases:
            if alias not in argument.VALID_ARGUMENTS:
                alias_list.append(alias)
            elif given_alias_list:
                raise CommandSpecError('Each alias in the list given must be valid')
            else:
                break

        if given_alias_list:
            return alias_list, 1

        return alias_list, len(alias_list)


class CommandEvent:

    def __init__(self, bot, command, args, message):
        self.bot = bot
        self.event_loop = self.bot.loop
        self.command = command  # Command class of the initiated command
        self.args = args  # Raw arguments given to the command
        self.message = message  # Discord message object that initiated the command
        self.channel = self.message.channel
        self.author = self.message.author
        self.server = self.message.server

    async def reply(self, message):
        if message is not None:
            await self.bot.send_message(self.channel, message)
