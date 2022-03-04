import nextcord


async def channel_containing_name(guild, name):
    if guild is not None and name is not None:
        return nextcord.utils.find(lambda c: name in c.name, guild.channels)
    return None


async def clear_channel(ctx, channel, *, limit=10, check=None, bulk=True, delay=None):
    await channel.purge(limit=limit, check=lambda m: not m.pinned and (check is None or check(m)), bulk=bulk)
    if delay is not None and ctx.message.channel.id != channel.id:
        await ctx.message.delete(delay=delay)
