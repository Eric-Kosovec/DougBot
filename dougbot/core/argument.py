
VALID_ARGUMENTS = [str, float, bool, int]


class Argument:

    # TODO ALLOW FOR CUSTOM TYPES - EXPAND PARSER

    def __init__(self, arg_type, optional):
        if arg_type not in VALID_ARGUMENTS:
            raise TypeError('Bad type')
        if optional is None or type(optional) != bool:
            raise TypeError('Optional can only be one of True or False')
        self.arg_type = arg_type
        self.optional = optional

    def __str__(self):
        return f'({self.arg_type}, {self.optional})'

    def __repr__(self):
        return f'Argument({self.arg_type}, {self.optional})'
