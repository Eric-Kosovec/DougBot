from plugins.audio import soundplayer

# NOTE: ALL TAKES PLACE WITHIN SERVER'S RESPECTIVE SOUNDPLAYER

ALIASES = ["play"]

sp = soundplayer.SoundPlayer()

async def run(alias, message, args, client):
    await ALIAS_TO_METHOD[alias](message, args, client)


# WILL ADD TO QUEUE (WITH START/END TIMESTAMP)
async def music_queue(message, args, client):
    if len(args) <= 0:
        return

    if "youtube.com" not in args[0]:
        return

    return


# END THE CURRENTLY PLAYING AUDIO (SOFT STOP, IDEALLY)
async def music_stop(message, args, client):
    return


# PLAY NEXT IN QUEUE
async def music_skip(message, args, client):
    return


# REMOVE ALL SONGS
async def music_clear(message, args, client):
    return


async def music_ffw(message, args, client):
    return


# START PLAYING FROM THE QUEUE - DON'T PLAY IF ALREADY PLAYING
async def music_play(message, args, client):
    await music_join(message, client)
    player = await client.voice_client_in(message.server).create_ytdl_player(
        'https://www.youtube.com/watch?v=dREbzlgmuZg')
    player.start()


async def music_volume_change(message, args, client):
    return


# DISPLAY VOLUME
async def music_current_volume(message, args, client):
    return


async def music_curr_playing(message, args, client):
    return


async def music_join(message, args, client):
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


async def music_leave(message, args, client):
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


ALIAS_TO_METHOD = {"join": music_join,
                   "leave": music_leave,
                   "play": music_play}
