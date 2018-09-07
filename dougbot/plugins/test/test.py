from dougbot.plugins.plugin import Plugin


class Test(Plugin):

    _TEST_MESSAGE = 'This is a test.'

    def __init__(self):
        super().__init__()

    @Plugin.command('test', int, float)
    async def print_test_message(self, event, i, f=5.0):
        await event.reply(f'int is {i}; float is {f}')
