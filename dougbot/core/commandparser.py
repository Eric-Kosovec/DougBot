import string


class Token:

    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def is_match(self, a_type):
        return a_type == self.token_type

    def __str__(self):
        return f'{self.token_type}: {self.value}'

    def __repr__(self):
        return f'Token({self.token_type}, {self.value})'


class CommandParser:

    def __init__(self, commands=None):
        self._command_map = {}
        if commands is not None:
            [self.add_command(c) for c in commands]

    def add_command(self, command):
        if command is None:
            raise TypeError('Attempted to add a None command to parser')

        for alias in command.aliases:
            if alias is None:
                raise TypeError("None alias in command's aliases list")
            if alias not in self._command_map:
                self._command_map[alias] = []
            self._command_map[alias].append(command)

    def parse_args(self, message):
        if message is None:
            raise TypeError('Message is None for parsing')

        cursor = message.find(' ')  # End of command alias
        if cursor <= 0:  # No arguments
            cursor = len(message)

        command_alias = message[:cursor]
        if command_alias not in self._command_map:
            raise TypeError('Command does not exist')

        tokens = []
        cursor += 1
        start = cursor  # Denote the start of the next token

        # Scan the user input into a series of tokens.
        while cursor < len(message):
            if self._peek(message, cursor) in string.whitespace:
                cursor += 1
                start = cursor
            else:
                cursor = self._argument(message, start, cursor, tokens)

        return self._matching_commands(command_alias, tokens)

    def _matching_commands(self, command_alias, tokens):
        matching_commands = []

        for command in self._command_map[command_alias]:
            command_arguments = self._match_command(tokens, command)
            if command_arguments is not None:
                matching_commands.append((command, command_arguments))

        return matching_commands

    @staticmethod
    def _match_command(tokens, command):
        # If argument is bool and token is one of float, int, then convert
        # If argument is str and token is one of float, int, then convert
        # If argument is optional, then move to next argument if no match
        if tokens is None or command is None:
            raise TypeError('Match command was given a None value')

        print(tokens)

        arguments = command.arguments

        # If there are no tokens, all arguments for the command must be optional to actually match
        if len(tokens) <= 0 < len(arguments):
            found_non_optional = False
            for arg in arguments:
                if not arg.optional:
                    found_non_optional = True
                    break
            if found_non_optional:
                return None
        elif len(arguments) <= 0 < len(tokens):  # Command needs no arguments, but some were given
            return None

        # All optional arguments must be at the end of the arguments, so the same index for both, as all of tokens must
        # be matched up until optional arguments
        arg_values = []
        i = 0
        while i < len(arguments) and i < len(tokens):
            if arguments[i].arg_type == tokens[i].token_type:
                arg_values.append(tokens[i].value)
            elif arguments[i].arg_type in [bool, int, float] and tokens[i].token_type != str:
                arg_values.append(arguments[i].arg_type(tokens[i].value))
            elif arguments[i].arg_type == str:  # Take the rest of the tokens as the string
                complete_str = ''
                while i < len(tokens):
                    complete_str += str(tokens[i].value) + ' '
                    i += 1
                arg_values.append(complete_str.strip())
            else:  # Not a match
                return None
            i += 1

        if i < len(tokens):  # Not all tokens have been consumed, so doesn't match
            return None

        print(arg_values)

        return arg_values

    def _argument(self, message, start, cursor, tokens):
        if message is None or start is None or cursor is None or tokens is None:
            raise TypeError('None type encountered in argument parsing')

        if start >= len(message) or start > cursor or cursor >= len(message):
            return cursor

        # Attempt a number match
        cursor = self._number(message, start, cursor, tokens)

        if cursor == start:  # Didn't match a number, so match a string
            cursor = self._string(message, start, tokens)

        return cursor

    def _number(self, message, start, cursor, tokens):
        if message is None or start is None or cursor is None or tokens is None:
            raise TypeError('None type encountered in number parsing')

        while cursor < len(message) and self._peek(message, cursor) in string.digits:
            cursor += 1

        token_type = int

        # At this point, it could be either the decimal for a float or the start of a separate type - or end of string
        if self._peek(message, cursor) == '.' and self._peek_next(message, cursor) in string.digits:
            token_type = float
            cursor += 1  # Consume the '.'

            while cursor < len(message) and self._peek(message, cursor) in string.digits:
                cursor += 1

        # A float without the end component
        elif self._peek(message, cursor) == '.' and \
                (self._peek_next(message, cursor) in string.whitespace or cursor + 1 == len(message)):
            token_type = float
            cursor += 1  # Consume the '.'

        # Doesn't match a number
        if cursor < len(message) and self._peek(message, cursor) not in string.whitespace:
            return start

        tokens.append(Token(token_type, token_type(message[start:cursor])))

        return cursor

    @staticmethod
    def _string(message, start, tokens):
        if message is None or start is None or tokens is None:
            raise TypeError('None type encountered in string parsing')
        tokens.append(Token(str, message[start:]))
        return len(message)

    @staticmethod
    def _peek(message, cursor):
        if message is None or cursor >= len(message):
            return '\0'
        return message[cursor]

    @staticmethod
    def _peek_next(message, cursor):
        if message is None or cursor + 1 >= len(message):
            return '\0'
        return message[cursor + 1]
