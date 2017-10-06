import os

from dougbot.core.util import queue
from dougbot.plugins import voicecomms

ALIASES = ['sb', 'sbclips', 'sbnext', 'sbstop', 'sbvolume', 'sbresume', 'sbpause']


class ServerSoundboard:
    def __init__(self):
        self.playing = False
        self.player = None
        self.queue = queue.Queue()
        self.voice = None
        self.volume = 1.0
        self.client = None
        self.message = None


server_sb = ServerSoundboard()

CLIPS_DIR = os.path.dirname(os.path.dirname(__file__))
CLIPS_DIR = os.path.join(CLIPS_DIR, 'resources', 'sbclips')


async def run(alias, message, args, client):
    if alias == 'sbclips':
        await soundboard_clips(message, client)
    elif alias == 'sb':
        if len(args) <= 0:
            return

        clip = ''
        for arg in args:
            clip = clip + arg

        await soundboard_play(clip, message, client)
    elif alias == 'sbstop':
        await soundboard_stop(message, client)
    elif alias == 'sbpause':
        await soundboard_pause()
    elif alias == 'sbresume':
        await soundboard_resume()
    elif alias == 'sbvolume':
        if len(args) <= 0:
            await client.send_message(message.channel, server_sb.volume * 100.0)
            return
        await soundboard_volume(float(args[0]))
    elif alias == 'sbnext':
        await soundboard_next()


async def soundboard_stop(message, client):
    server_sb.queue.clear()
    if server_sb.player is not None:
        server_sb.player.stop()


# TODO ADD PAUSED FLAG?
async def soundboard_pause():
    if server_sb.player is not None:
        server_sb.player.pause()


async def soundboard_volume(vol):
    if vol < 0.0:
        vol = 0.0
    elif vol > 200.0:
        vol = 200.0
    server_sb.volume = vol / 100.0
    if server_sb.player is not None:
        server_sb.player.volume = server_sb.volume


async def soundboard_resume():
    if server_sb.player is not None:
        server_sb.player.resume()


async def soundboard_next():
    if server_sb.player is not None:
        server_sb.player.stop()


async def soundboard_clips(message, client):
    cliplist = []

    for file in os.listdir(CLIPS_DIR):
        if file.endswith('.mp3'):
            cliplist.append(file[:file.find('.mp3')])

    msg = 'Soundboard Clips:\n\n'

    for clip in cliplist:
        msg = msg + clip + '\n'

    await client.send_message(message.channel, msg)


async def soundboard_play(clip, message, client):
    clip_path = os.path.join(CLIPS_DIR, '%s.mp3' % clip)

    try:
        with open(clip_path):
            pass
    except IOError:
        await client.confusion(message)
        return

    if server_sb.playing:
        server_sb.queue.enqueue(clip_path)
        return

    server_sb.voice = client.voice_client_in(message.server)
    if server_sb.voice is None:
        server_sb.voice = await voicecomms.join(message, client)

    server_sb.playing = True

    # Grab the file requested
    server_sb.player = server_sb.voice.create_ffmpeg_player(clip_path, after=soundboard_finished)
    server_sb.player.volume = server_sb.volume
    server_sb.player.start()


def soundboard_finished():
    if server_sb.queue.size() > 0:
        file = server_sb.queue.dequeue()
        server_sb.player = server_sb.voice.create_ffmpeg_player(file, after=soundboard_finished)
        server_sb.player.volume = server_sb.volume
        server_sb.player.start()
    else:
        server_sb.playing = False
