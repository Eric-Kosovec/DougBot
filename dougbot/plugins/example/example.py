from dougbot.plugins.plugin import Plugin


class Example(Plugin):

    # Event objects are required to be the first argument.

    # Only an alias, no arguments
    @Plugin.command('test')
    def example1(self, event):
        return

    # Multiple aliases
    @Plugin.command('test1', 'test2')
    def example2(self, event):
        return

    # Multiple aliases
    @Plugin.command(['test1', 'test2'])
    def example3(self, event):
        return

    # Can do any of the above with arguments

    # One argument
    @Plugin.command('test', int)
    def example4(self, event, in_int):
        return

    # Multiple arguments - Only one string allowed and at end
    @Plugin.command('test', int, float, str)
    def example5(self, event, in_int, in_float, in_str):
        return

    # Optional arguments - the ones with a default value - are acceptable after non-default arguments
    @Plugin.command('test', int, float)
    def example6(self, event, in_int, in_float=3.0):
        return
