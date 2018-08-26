
class Listener:

    def __init__(self, plugin, func, *args, **kwargs):
        self.plugin = plugin
        self.func = func
        self.args = args
        self.kwargs = kwargs

