from dougbot.plugins.plugin import Plugin


class ListenTest(Plugin):

    def __init__(self):
        super().__init__()
        return

    @Plugin.listen('tester')
    async def listening(self):
        print('listening function')
