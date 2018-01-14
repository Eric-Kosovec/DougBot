from dougbot.plugins.plugin import Plugin


class MonsterHunt(Plugin):

    def __init__(self):
        self.environment = None
        super().__init__()

    @Plugin.command('hunt')
    async def hunt(self, event):
        await event.bot.send_message(event.message.channel, 'Hunting for monsters, huh?')
        # Generate game world, if one is not already

        if self.environment is None:
            await event.bot.send_message(event.message.channel, 'Generating game world...')
            # Generate
            await event.bot.send_message(event.message.channel, 'Generated.')

        # Allocate weaponry to user
        await event.bot.send_message(event.message.channel, f'Assigning weaponry to user {event.message.author.name}.')

