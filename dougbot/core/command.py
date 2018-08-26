from enum import Enum

import dougbot.core.argument as argument
from dougbot.core.argument import ArgumentSet
from dougbot.util.customargparse import NoErrorMessageArgumentParser


class CommandLevel(Enum):
    OWNER = 5
    BLOCKED = 4
    ADMIN = 3
    USER = 2
    NULL = 1


class CommandError(Exception):

    def __init__(self, msg):
        self.msg = msg


class Command:

    _PARSER_PROG_NAME = 'COMMAND'
    _PARSER_COMMAND_ARG_NAME = 'command_name'
    _ARG_NAME = 'arg'

    def __init__(self, plugin, func, *args, **kwargs):
        self.plugin = plugin
        self.func = func
        self.args = args
        self.kwargs = kwargs

        self.aliases, args_start = self._parse_aliases(*args)
        self.argset = self._parse_arguments(args_start, *args)
        self.parser = self._create_parser(self.aliases, self.argset)

    async def execute(self, event):
        await self.func(event, *event.args)

    def is_match(self, message):
        if message is None:
            return False

        try:
            result = self.parser.parse_args(message.split())
        except SystemExit:
            result = None

        if result is None:
            return False

        return True

    def extract_arguments(self, message):
        if not self.is_match(message):
            return {}

        args = self.parser.parse_args(message.split())

        argcount = 0

        arglist = []

        args = vars(args)

        while True:
            try:
                arglist.append(args[f'{self._ARG_NAME}{argcount}'])
                argcount += 1
            except KeyError:
                break

        return arglist

    def _create_parser(self, aliases, argset):
        parser = NoErrorMessageArgumentParser(prog=self._PARSER_PROG_NAME)

        # First required argument will be one of the command's aliases
        parser.add_argument(self._PARSER_COMMAND_ARG_NAME, nargs=1, choices=aliases)

        argcount = 0

        for arg in argset:
            kwargs = {'type': arg.type}
            if arg.required:
                kwargs['nargs'] = '?'
                kwargs['default'] = None
            parser.add_argument(f'{self._ARG_NAME}{argcount}', **kwargs)
            argcount += 1

        return parser

    @staticmethod
    def _parse_arguments(args_start, *args):
        if args_start <= 0 or args is None:
            return None

        return ArgumentSet(args[args_start:])

    @staticmethod
    def _parse_aliases(*args):
        if args is None:
            return []

        end = 0

        if len(args) > 0 and type(args[0]) == list:
            return args[0], end + 1

        aliases = []

        for arg in args:
            if arg not in argument.ARGUMENTS:
                end += 1
                aliases.append(arg)
            else:
                break

        return aliases, end


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
        if not message:
            return
        await self.bot.send_message(self.channel, message)
