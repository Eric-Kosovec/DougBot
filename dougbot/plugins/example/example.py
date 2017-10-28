from dougbot.plugins.plugin import Plugin


class Example(Plugin):

    @Plugin.command('test', 'best', '<content:str>')
    def test(self, event, content):
        print("Tested")
        return

    @Plugin.command('test2', '<the:float>')
    def test2(self, event, the):
        print("Test2")
        return
