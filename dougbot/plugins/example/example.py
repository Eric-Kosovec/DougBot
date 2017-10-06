from dougbot.plugins.plugin import Plugin


class Example(Plugin):
    def __init__(self):
        super().__init__()

    @Plugin.command('test', '<content:str>', '<love:int>')
    def test(self):
        print("Tested")
        return

    @Plugin.command('test2', '<the:float>')
    def test2(self):
        print("Test2")
        return


if __name__ == '__main__':
    ex = Example()
