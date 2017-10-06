
TYPE_MAP = {
    'int': int,
    'str': str,
    'float': float,
    'bool': bool
}

TYPE_TO_REGEX = {
    int: r'[-]?\d+',
    str: r'.+',
    float: r'[-]?(?<![\.\d])[0-9]+(?![\.\d])',
    bool: r'True|False|true|false|0|1'
}

# TODO ALLOW FOR UNDERSCORES
_ARG_REGEX = r'<[a-zA-Z]+[0-9]*:(str|int|float|bool)(...)?>'

_WHITESPACE_MATCH = r'\s+'
_WHITESPACE_MATCH_OPTIONAL = r'\s*'


def to_bool(st):
    conv = False
    if st.lower() == 'true' or st.lower() == '1':
        conv = True
    return conv

if __name__ == '__main__':
    expr = 'hello 5.0 s 5 the'
    reg = '^' + r'(?=the|hello)' + TYPE_TO_REGEX[float] + TYPE_TO_REGEX[str] + TYPE_TO_REGEX[int] + TYPE_TO_REGEX[str] + '$'
    #reg = r'(?=the|hello)' + '\s+.+'
    import re
    p = re.compile(reg)
    m = p.findall(expr)
    print(m)


class Argument:

    def __init__(self, arg):
        self.name = None
        self.type = None
        self.required = True
        self._parse(arg)

    def _parse(self, arg):
        split_arg = arg[len('<'):len(arg) - len('>')].split(':')
        arg_name = split_arg[0]
        arg_type = split_arg[1]
        self.name = arg_name
        self.type = TYPE_MAP[arg_type]
        print('Arg name: %s; type: %s' % (arg_name, arg_type))

    '''
        Get regex representing the argument
    '''
    def get_regex(self):
        return TYPE_TO_REGEX[self.type]


class ArgumentSet:

    def __init__(self, args):
        self.args = args
        self.arg_objs = []
        self._parse()

    def _parse(self):
        for arg in self.args:
            self.arg_objs.append(Argument(arg))

    def __len__(self):
        return len(self.arg_objs)

    def length(self):
        return len(self)

    def get_regex(self):
        arg_set_regex = ''
        space_match = ''
        for arg_class in self.arg_objs:
            arg_set_regex += space_match + arg_class.get_regex()
            space_match = _WHITESPACE_MATCH
        return arg_set_regex


class Parser:

    def __init__(self):
        return
