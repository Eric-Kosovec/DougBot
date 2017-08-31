import os
import sys

import plugins.voicecomms
from util import queue

ALIASES = ["sb", "sbclips", "sbaddclip"]

playing = False
# playing_lock = threading.Lock()
# TODO Determine if synchronization is required.
#sound_queue_lock = threading.Lock()
sound_queue = queue.Queue()

voice = None

sys.path.append("resources/sbclips")

async def run(alias, message, args, client):
    global playing

    if alias == "sbclips":
        await _soundboard_clipslist(message, client)
        return
    elif alias == "sbaddclip":
        await _soundboard_add_clip("", message, client)
        return

    if len(args) <= 0:
        return

    clip = ""
    for arg in args:
        clip = clip + arg

    await _soundboard_play(clip, message, client)


async def _soundboard_clipslist(message, client):
    cliplist = []

    for file in os.listdir("resources/sbclips"):
        if file.endswith(".mp3"):
            cliplist.append(file[:file.find(".")])

    msg = "Soundboard Clips:\n\n"

    for clip in cliplist:
        msg = msg + clip + "\n"

    await client.send_message(message.channel, msg)


async def _soundboard_play(clip, message, client):
    global playing, voice

    try:
        with open("resources/sbclips/%s.mp3" % clip) as f:
            pass
    except IOError:
        await client.add_reaction(message, "❓")
        return

    if playing:
        sound_queue.enqueue("resources/sbclips/%s.mp3" % clip)
        return

    voice = client.voice_client_in(message.server)
    if voice is None:
        voice = await plugins.voicecomms.join(message, client)

    playing = True

    # Grab the file requested
    player = voice.create_ffmpeg_player("resources/sbclips/%s.mp3" % clip, after=_soundboard_finished)
    player.start()

    return


def _soundboard_finished():
    global playing

    if sound_queue.size() > 0:
        file = sound_queue.dequeue()
        player = voice.create_ffmpeg_player(file, after=_soundboard_finished)
        player.start()
    else:
        playing = False


async def _soundboard_add_clip(url, message, client):
    await client.send_message(message.channel, "You will one day add mp3 links.")


def cleanup():
    # TODO ?
    return
