from dougbot.plugins.plugin import Plugin


class Test(Plugin):

    def __init__(self):
        super().__init__()
        return

    @Plugin.command('Meth')
    def mymethod(self, event):
        return