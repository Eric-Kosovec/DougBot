import nextcord


async def channel_containing_name(guild, name):
    if guild is not None and name is not None:
        return nextcord.utils.find(lambda c: name in c.name, guild.channels)
    return None
