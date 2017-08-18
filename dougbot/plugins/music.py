ALIASES = ["join", "leave", "play"]


async def run(alias, message, args, client):
    await ALIAS_TO_METHOD[alias](message, client)


async def music_join(message, client):
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

    await client.join_voice_channel(user_voice_channel)


async def music_leave(message, client):
    # Don't leave channel if this was a private message, unless it's from the owner.
    if message.channel.is_private:
        return

    # Message is not from a user within a voice channel.
    if message.author.voice.voice_channel is None:
        return

    # Get the VoiceClient object of the bot's from the server the message was sent from.
    bot_voice_client = client.voice_client_in(message.server)

    # Bot is not in a voice channel on the server.
    if bot_voice_client is None:
        return

    await bot_voice_client.disconnect()


async def music_play(message, client):
    await music_join(message, client)
    player = await client.voice_client_in(message.server).create_ytdl_player(
        'https://www.youtube.com/watch?v=dREbzlgmuZg')
    player.start()


ALIAS_TO_METHOD = {"join": music_join,
                   "leave": music_leave,
                   "play": music_play}

# Defines all music commands and soundplayers for servers

# NOTE: ALL TAKES PLACE WITHIN SERVER'S RESPECTIVE SOUNDPLAYER
# PLAY WILL START PLAYING FROM THE QUEUE - DON'T PLAY IF ALREADY PLAYING
# QUEUE WILL ADD TO QUEUE (WITH START/END TIMESTAMP)
# STOP WILL END THE CURRENTLY PLAYING AUDIO (SOFT STOP, IDEALLY)
# NEXT WILL PLAY NEXT IN QUEUE
# CLEAR QUEUE WILL REMOVE ALL SONGS
# REMOVE LINK WILL REMOVE THE GIVEN LINK FROM QUEUE
# REMOVE BY ITSELF WILL REMOVE CURRENT PLAYING OR FRONT OF QUEUE ITEM
# VOLUME # CHANGES VOLUME
# CURR VOLUME DISPLAY VOLUME
# FFW
# SKIP ONTO NEXT TRACK
# LEAVE WILL MAKE IT STOP TRACK, CLEAR QUEUE, LEAVE
# JOIN PLAYS CURRENT QUEUE
# NOW PLAYING
# DEQUEUE # ?
