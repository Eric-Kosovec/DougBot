ALIASES = ["play"]


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
    return

async def music_volume_change(message, args, client):
    return


# DISPLAY VOLUME
async def music_current_volume(message, args, client):
    return


async def music_curr_playing(message, args, client):
    return


ALIAS_TO_METHOD = {"play": music_play}
