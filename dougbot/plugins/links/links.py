from dougbot.plugins.plugin import Plugin


class Links(Plugin):

    _SDT_LINK = 'https://cytu.be/r/SadDoug'

    @Plugin.command('sdt', 'cytube')
    async def theater_link(self, event):
        await event.reply(self._SDT_LINK)

    @Plugin.command('git', 'github')
    async def github_link(self, event):
        await event.reply(event.bot.config.source_code)
