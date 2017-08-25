import os
import sys
import threading

import plugins.voicecomms
from util import queue

ALIASES = ["sb", "sbclips"]

playing = False
playing_lock = threading.Lock()

sound_queue_lock = threading.Lock()
sound_queue = queue.Queue()

voice = None

sys.path.append("resources/sbclips")

async def run(alias, message, args, client):
    global playing

    if alias == "sbclips":
        await _soundboard_clipslist(message, client)
        return

    if len(args) <= 0:
        return

    await _soundboard_play(args[0], message, client)


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

    print("TRYING TO ACQUIRE LOCK")
    print(threading.current_thread())

    playing_lock.acquire()

    print("ACQUIRED LOCK")

    if playing:
        print("IS PLAYING")
        sound_queue_lock.acquire()
        sound_queue.enqueue("resources/sbclips/%s.mp3" % clip)
        sound_queue_lock.release()
        playing_lock.release()
        return

    voice = client.voice_client_in(message.server)
    if voice is None:
        voice = await plugins.voicecomms.join(message, client)

    print("PLAYER")

    # Grab the file requested
    player = voice.create_ffmpeg_player("resources/sbclips/%s.mp3" % clip, after=_soundboard_finished)
    player.start()

    playing = True
    playing_lock.release()
    return


def _soundboard_finished():
    global playing

    playing_lock.acquire()
    sound_queue_lock.acquire()

    if sound_queue.size() > 0:
        file = sound_queue.dequeue()
        player = voice.create_ffmpeg_player(file, after=_soundboard_finished)
        player.start()
    else:
        playing = False

    sound_queue_lock.release()
    playing_lock.release()


def cleanup():
    return
