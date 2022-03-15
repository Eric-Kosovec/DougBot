import nextcord


async def channel_name_like(guild, name):
    return nextcord.utils.find(lambda c: name in c.name, guild.channels)


async def clear_channel(channel, *, limit=10, check=None, bulk=True):
    await channel.purge(limit=limit, check=lambda m: not m.pinned and (check is None or check(m)), bulk=bulk)
