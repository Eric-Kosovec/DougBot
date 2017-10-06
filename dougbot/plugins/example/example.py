from dougbot.plugins.plugin import Plugin


class Example(Plugin):
    def __init__(self):
        super().__init__()

    @Plugin.command('test', 'best', '<content:str>', '<love:int>')
    def test(self, event, cotent, love):
        print("Tested")
        return

    @Plugin.command('test2', '<the:float>')
    def test2(self, event, the):
        print("Test2")
        return


if __name__ == '__main__':
    ex = Example()
