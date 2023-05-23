import nextcord

from dougbot.core.bot import DougBot


async def join_voice_channel(channel, bot: DougBot):
    voice_client = await voice_in(channel, bot)
    return await channel.connect() if voice_client is None else voice_client


async def voice_in(channel, bot: DougBot):
    return nextcord.utils.find(lambda vc: vc.channel.id == channel.id, bot.voice_clients)
