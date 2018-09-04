from dougbot.plugins.plugin import Plugin


class Test(Plugin):

    _TEST_MESSAGE = 'This is a test.'

    def __init__(self):
        super().__init__()

    @Plugin.command('test')
    async def print_test_message(self, event):
        await event.reply(self._TEST_MESSAGE)
