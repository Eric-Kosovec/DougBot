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

    def __init__(self):
        self._command_map = {}

    def add_command(self, command):
        if command is None:
            return

        for alias in command.aliases:
            if alias not in self._command_map:
                self._command_map[alias] = []
            self._command_map[alias].append(command)

    def parse_args(self, message):
        if message is None:
            return None

        tokens = []

        cursor = message.find(' ')  # End of command alias

        if cursor <= 0:  # No arguments
            cursor = len(message)

        command_alias = message[:cursor]

        if command_alias not in self._command_map:
            raise TypeError('Command does not exist')

        cursor += 1
        start = cursor  # Denote the start of the next token

        while cursor < len(message):
            if self._peek(message, cursor) in string.digits:
                cursor = self._number(message, start, cursor, tokens)  # Tokenize the number
            elif self._peek(message, cursor) in string.whitespace:
                cursor += 1
                start = cursor
            else:
                cursor = self._string(message, start, tokens)  # Tokenize the string

        print(tokens)

        alias_commands = self._command_map[command_alias]

        matching_commands = []

        for command in alias_commands:
            command_arguments = self._match_command(tokens, command)
            if command_arguments is not None:
                matching_commands.append((command, command_arguments))

        return matching_commands

    # TODO ALLOW FOR COMMANDS WITH SAME ALIAS TO HAVE DIFFERING ARGUMENTS, EG OPTIONAL DIFFERENCES
    @staticmethod
    def _match_command(tokens, command):
        # If argument is bool and token is one of float, int, then convert
        # If argument is str and token is one of float, int, then convert
        # If argument is optional, then move to next argument if no match

        arguments = command.arguments
        arg_values = []

        # If no tokens, make sure there is at least one non-optional
        if len(tokens) <= 0 < len(arguments):
            found_non_optional = False
            for arg in arguments:
                print(arg)
                if not arg.optional:
                    found_non_optional = True
                    break
            if found_non_optional:
                return None

        i = 0
        j = 0
        while i < len(arguments) and j < len(tokens):
            if arguments[i].arg_type == tokens[j].token_type:
                arg_values.append(tokens[j].value)
                j += 1
            elif arguments[i].optional:
                pass
            elif arguments[i].arg_type == bool and tokens[j].token_type in [float, int]:
                arg_values.append(bool(tokens[j].value))
                j += 1
            elif arguments[i].arg_type == int and tokens[j].token_type == float:
                arg_values.append(int(tokens[j].value))
                j += 1
            elif arguments[i].arg_type == float and tokens[j].token_type == int:
                arg_values.append(float(tokens[j].value))
                j += 1
            elif arguments[i].arg_type == str:  # Take the rest of the tokens as the string
                complete_str = ''
                while j < len(tokens):
                    complete_str += str(tokens[j].value) + ' '
                    j += 1
                arg_values.append(complete_str.strip())
            else:  # Not a match
                return None
            i += 1

        print(arg_values)

        return arg_values

    def _number(self, message, start, cursor, tokens):
        is_float = False

        while cursor < len(message) and self._peek(message, cursor) in string.digits:
            cursor += 1

        # At this point, it could be either the decimal for a float or the start of a separate type
        if self._peek(message, cursor) == '.' and self._peek_next(message, cursor) in string.digits:
            is_float = True
            cursor += 1  # Consume the '.'

            while cursor < len(message) and self._peek(message, cursor) in string.digits:
                cursor += 1

        token_type = int

        if is_float:
            token_type = float

        tokens.append(Token(token_type, token_type(message[start:cursor])))

        return cursor

    @staticmethod
    # TODO MAYBE MATCH SINGLE WORDS IF MULTIPLE STRING ARGUMENTS UP TO FINAL STRING, THEN USE REST
    def _string(message, start, tokens):
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
