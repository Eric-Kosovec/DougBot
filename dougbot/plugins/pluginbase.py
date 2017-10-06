import abc


class PluginBase(metaclass=abc.ABCMeta):

    def __init__(self, func_map):
        self.func_map = func_map

    async def run(self, alias, message, args, client):
        await self.func_map[alias](message, args, client)

    @abc.abstractmethod
    async def help(self, alias, message, args, client):
        return

    @abc.abstractmethod
    async def cleanup(self, message, args, client):
        return
