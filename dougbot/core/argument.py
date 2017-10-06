
TYPE_MAP = {
    'int': int,
    'str': str,
    'float': float,
    'bool': bool
}

TYPE_TO_REGEX = {
    int: r'[-]?\d+',
    str: r'.+',
    float: r'[-]?\d*[.]\d+',
    bool: r'True|False|true|false|0|1'
}

# TODO ALLOW FOR UNDERSCORES
ARG_REGEX = r'<[a-zA-Z]+[0-9]*:(str|int|float|bool)(...)?>'

WHITESPACE_MATCH = r'\s+'
WHITESPACE_MATCH_OPTIONAL = r'\s*'


def to_bool(st):
    conv = False
    if st.lower() == 'true' or st.lower() == '1':
        conv = True
    return conv

'''if __name__ == '__main__':
    expr = 'hello 5.0 tree'
    #reg = r'^(hello|there)\s+\d+\s+.+$'
    reg = r'^' + _WHITESPACE_MATCH_OPTIONAL + r'(hello|there)' + _WHITESPACE_MATCH + TYPE_TO_REGEX[float] + _WHITESPACE_MATCH + TYPE_TO_REGEX[str] + _WHITESPACE_MATCH_OPTIONAL + '$'
    import re
    p = re.compile(reg)
    m = p.fullmatch(expr)
    if m is None:
        print("NO MATCH")
    else:
        print(expr[m.start():m.end()])
        print(m)
'''


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
            space_match = WHITESPACE_MATCH
        return arg_set_regex
