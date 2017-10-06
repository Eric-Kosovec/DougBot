from plugins.pluginbase import *


class Example(PluginBase):

    def __init__(self):
        func_map = {'help': self.send_help, 'aids': self.aids}
        super().__init__(func_map)

    async def send_help(self, message, args, client):
        await client.send_message(message.channel, "SENDING HELP")

    async def aids(self, message, args, client):
        await client.send_message(message.channel, "AIDS")

    async def help(self, alias, message, args, client):
        return

    async def cleanup(self, message, args, client):
        return
