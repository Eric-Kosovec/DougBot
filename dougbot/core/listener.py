from dougbot.plugins.listento import ListenTo


class ListenerError(Exception):

    def __init__(self, msg):
        self.msg = msg


class ListenerSpecError(ListenerError):

    def __init__(self, msg):
        super().__init__(msg)


class Listener:

    def __init__(self, plugin, func, *args, **kwargs):
        self._validate_spec(*args)
        self.plugin = plugin
        self.func = func

        self.listening = True
        if len(args) == 2:
            self.listening = bool(args[1])

        self.args = args[0]
        self.kwargs = kwargs

    def is_listening(self):
        return self.listening

    def toggle_listening(self):
        self.listening = not self.listening
        return not self.listening

    async def execute(self, event):
        try:
            await self.func(event, *event.args)
        except Exception as e:
            raise ListenerError(e)

    @staticmethod
    def _validate_spec(*args):
        if args is None:
            raise ListenerSpecError('Listener args was None')
        if len(args) < 0 or len(args) > 2:
            raise ListenerSpecError('Listener specification can only have one argument')
        if type(args[0]) != ListenTo:
            raise ListenerSpecError(f"Listener specification argument '{args[0]}' must be a ListenTo type")
        if len(args) == 2 and type(args[1]) not in [int, float, bool]:
            raise ListenerSpecError(f"Listener specification argument '{args[1]}' must be a numerical or bool type")


class ListenerEvent:

    def __init__(self, bot, listener, args):
        self.bot = bot
        self.event_loop = self.bot.loop
        self.listener = listener
        self.args = args
