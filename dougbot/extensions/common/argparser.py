
class ArgParser:

    _FALSE_BOOL_VALUES = [0, 0.0, 'F', 'f', 'False', 'false']

    _TRUE_BOOL_VALUES = [1, 1.0, 'T', 't', 'True', 'true']

    @classmethod
    def parse(cls, text, types=None):
        if types is None:
            types = [str]

        words = text.strip().split()
        tokens = cls._tokenize(words)
        return cls._parse(tokens, types)

    @classmethod
    def _parse(cls, tokens, types):
        arguments = []

        j = 0
        for i, arg_type in enumerate(types):
            if arg_type == str:
                curr_arg = str(tokens[j])
                j += 1
                while j < len(tokens) and (i == len(types) - 1 and types[i] == str) or \
                        (i + 1 < len(types) and not cls._can_convert(tokens[j], types[i + 1])):
                    curr_arg += f' {tokens[j]}'
                    j += 1
                arguments.append(curr_arg)

            elif arg_type == bool:
                arguments.append(cls._as_bool(tokens[j]))
                j += 1

            elif arg_type in [float, int]:
                arguments.append(arg_type(tokens[j]))
                j += 1

            else:
                return None

        if j < len(tokens):
            return None

        return arguments

    @classmethod
    def _tokenize(cls, words):
        return [cls._tokenize_word(word) for word in words]

    @classmethod
    def _tokenize_word(cls, word):
        casted = None
        for cast_type in [float, int]:
            try:
                casted = cast_type(word)
            except ValueError:
                pass
        return word if casted is None else casted

    @classmethod
    def _can_convert(cls, token, to_type):
        return to_type == type(token) or to_type == bool and cls._is_booly(token) or \
               (type(token) in [float, int] and to_type in [float, int])

    @classmethod
    def _is_booly(cls, token):
        return token in cls._TRUE_BOOL_VALUES or cls._FALSE_BOOL_VALUES

    @classmethod
    def _as_bool(cls, token):
        return token in cls._TRUE_BOOL_VALUES
