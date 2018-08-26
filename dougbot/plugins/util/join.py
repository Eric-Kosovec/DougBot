# TODO MAYBE PUT INTO BOT - METHODS TO TELL IT TO JOIN A SPECIFIC PLACE


async def bot_join(event, callback=None, callback_async=False):
    if event is None or event.channel.is_private:
        return

    user_voice_channel = event.author.voice.voice_channel

    # Commander is not in a voice channel.
    if not user_voice_channel:
        return

    # Make sure bot isn't already in a voice channel on the server
    if event.bot.voice_client_in(event.server):
        return

    if callback is not None:
        if callback_async:
            await callback()
        else:
            callback()

    return await event.bot.join_voice_channel(user_voice_channel)


async def bot_leave(event, callback=None, callback_async=False):
    if event is None or event.channel.is_private:
        return

    bot_voice_client = event.bot.voice_client_in(event.server)

    if not _in_same_voice_channel(event):
        return

    if callback is not None:
        if callback_async:
            await callback()
        else:
            callback()

    await bot_voice_client.disconnect()


def _in_voice_channel(event):
    if not event:
        return False

    return event.bot.voice_client_in(event.server) is not None


def _in_same_voice_channel(event):
    if not event or not _in_voice_channel(event):
        return False

    bot_voice_client = event.bot.voice_client_in(event.server)

    if not event.author.voice:
        return False

    user_voice_channel = event.author.voice.voice_channel

    if not user_voice_channel:
        return False

    return bot_voice_client.channel.id == user_voice_channel.id
