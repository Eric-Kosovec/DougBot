
ARGUMENTS = ['int', 'int?', 'float', 'float?', 'bool', 'bool?', 'str', 'str?', int, float, bool, str]

OPTIONAL = '?'

TYPE_MAP = {
    'bool': bool,
    'int': int,
    'float': float,
    'str': str,
    bool: bool,
    int: int,
    float: float,
    str: str
}


class Argument:

    def __init__(self, arg):
        self.required = True
        self.type = None
        self._parse(arg)

    def _parse(self, arg):
        if arg not in ARGUMENTS:
            return
        if type(arg) == str and arg.endswith(OPTIONAL):
            self.required = False
            arg = arg[:-len(OPTIONAL)]
        self.type = TYPE_MAP[arg]


class ArgumentSet:

    def __init__(self, args):
        self.arguments = self._generate(args)

    @staticmethod
    def _generate(args):
        arguments = []
        for arg in args:
            arguments.append(Argument(arg))
        return arguments

    def __iter__(self):
        self._iterindex = 0
        return self

    def __next__(self):
        if self._iterindex >= len(self) or self._iterindex < 0:
            raise StopIteration
        item = self.arguments[self._iterindex]
        self._iterindex += 1
        return item

    def __len__(self):
        return len(self.arguments)
