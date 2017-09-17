from dougbot.plugins import soundboard

ALIASES = ['join', 'leave']


async def run(alias, message, args, client):
    await COMMAND_MAP[alias](message, client)
    return


async def join(message, client):
    if message is None or client is None:
        return

    # Don't join a channel if this was a private message, unless it's from the owner.
    if message.channel.is_private:
        return

    user_voice_channel = message.author.voice.voice_channel

    # User is not in a voice channel, ignore them.
    if user_voice_channel is None:
        return

    # Check if we are already in a channel on the server
    if client.voice_client_in(message.server) is not None:
        return

    voice = await client.join_voice_channel(user_voice_channel)

    return voice


async def leave(message, client):
    if message is None or client is None:
        return

    # Don't leave channel if this was a private message, unless it's from the owner.
    if message is not None and message.channel.is_private:
        return

    # Message is not from a user within a voice channel.
    if message is not None and message.author.voice.voice_channel is None:
        return

    # Get the VoiceClient object of the bot's from the server the message was sent from.
    bot_voice_client = client.voice_client_in(message.server)

    # Bot is not in a voice channel on the server.
    if bot_voice_client is None:
        return

    # User is not in the same voice channel as the bot.
    if not bot_voice_client.channel == message.author.voice.voice_channel:
        return

    # TODO GET RID OF NEEDING THIS
    soundboard.playing = False
    soundboard.voice = None

    await bot_voice_client.disconnect()


COMMAND_MAP = {'join': join, 'leave': leave}
