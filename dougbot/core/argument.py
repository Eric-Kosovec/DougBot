import re

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

TYPE_TO_REGEX_MATCHER = {
    int: re.compile(TYPE_TO_REGEX[int]),
    str: re.compile(TYPE_TO_REGEX[str]),
    float: re.compile(TYPE_TO_REGEX[float]),
    bool: re.compile(TYPE_TO_REGEX[bool])
}

ARG_REGEX = r'<[a-zA-Z]+[0-9]*([_]*[a-zA-Z]*[0-9]*)*:(str|int|float|bool)(...)?>'

WHITESPACE_MATCH = r'\s+'
WHITESPACE_MATCH_OPTIONAL = r'\s*'


def to_bool(st):
    conv = False
    if st.lower() == 'true' or st.lower() == '1':
        conv = True
    return conv


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

    '''
        Get regex representing the argument
    '''

    def get_regex(self):
        return TYPE_TO_REGEX[self.type]


class ArgumentSet:
    def __init__(self, args):
        '''

        :param args: Argument specification command should have
        '''
        self.args = args
        self.arg_objs = []
        self._generate()

    def _generate(self):
        for arg in self.args:
            self.arg_objs.append(Argument(arg))

    '''
        Parse the given string into this set
    '''

    def parse(self, args):
        split_args = args.split()

        command_name = split_args[0]

        parsed_args = {}

        cur_arg = 0
        cur_data = 1

        while cur_arg < len(self.arg_objs):
            cur_arg_name = self.arg_objs[cur_arg].name
            cur_arg_type = self.arg_objs[cur_arg].type
            value = None
            if cur_arg_type == bool:
                value = bool(split_args[cur_data])
                cur_data += 1
            elif cur_arg_type == int:
                value = int(split_args[cur_data])
                cur_data += 1
            elif cur_arg_type == float:
                value = float(split_args[cur_data])
                cur_data += 1
            elif cur_arg_type == str and cur_arg + 1 < len(self.arg_objs) and self.arg_objs[cur_arg + 1].type == str:
                value = str(split_args[cur_data])
                cur_data += 1
            elif cur_arg_type == str and cur_arg + 1 < len(self.arg_objs):
                # Create string until hitting a type of the next argument
                value = ''

                next_type = self._find_next_type(split_args, cur_arg_type, cur_data + 1)

                if next_type < 0:
                    str_end = len(split_args) - 1
                else:
                    str_end = next_type - 1

                space = ''
                while cur_data <= str_end:
                    value += space + split_args[cur_data]
                    cur_data += 1
                    space = ' '
            elif cur_arg_type == str:
                value = ''

                space = ''
                while cur_data < len(split_args):
                    value += space + split_args[cur_data]
                    cur_data += 1
                    space = ' '

            if not value:
                # TODO FAIL
                break

            # TODO Return in this form or in list?
            parsed_args[cur_arg_name] = value

            cur_arg += 1

        return parsed_args

    def _find_next_type(self, args, cur_type, start):
        next_type_idx = -1

        for i in range(start, len(args)):
            if self._determine_type(args[i]) != cur_type:
                next_type_idx = i
                break

        return next_type_idx

    @staticmethod
    def _determine_type(arg):
        if TYPE_TO_REGEX_MATCHER[bool].fullmatch(arg):
            return bool
        if TYPE_TO_REGEX_MATCHER[int].fullmatch(arg):
            return int
        if TYPE_TO_REGEX_MATCHER[float].fullmatch(arg):
            return float
        if TYPE_TO_REGEX_MATCHER[str].fullmatch(arg):
            return str
        return None

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
