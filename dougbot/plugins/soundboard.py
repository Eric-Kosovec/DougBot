import os

from dougbot.core.util import queue
from dougbot.plugins import voicecomms

ALIASES = ['sb', 'sbclips', 'sbaddclip']

playing = False

sound_queue = queue.Queue()

voice = None

clips_dir = os.path.dirname(os.path.dirname(__file__))
clips_dir = os.path.join(clips_dir, 'resources', 'sbclips')

async def run(alias, message, args, client):
    global playing

    if alias == 'sbclips':
        await _soundboard_clipslist(message, client)
        return
    elif alias == 'sbaddclip':
        await _soundboard_add_clip('', message, client)
        return

    # If here, must be command 'sb'

    if len(args) <= 0:
        return

    clip = ''
    for arg in args:
        clip = clip + arg

    await _soundboard_play(clip, message, client)


async def _soundboard_clipslist(message, client):
    cliplist = []

    for file in os.listdir(clips_dir):
        if file.endswith('.mp3'):
            cliplist.append(file[:file.find('.')])

    msg = 'Soundboard Clips:\n\n'

    for clip in cliplist:
        msg = msg + clip + '\n'

    await client.send_message(message.channel, msg)


async def _soundboard_play(clip, message, client):
    global playing, voice

    clip_path = os.path.join(clips_dir, '%s.mp3' % clip)

    try:
        with open(clip_path) as f:
            pass
    except IOError as e:
        await client.confusion(message)
        return

    if playing:
        sound_queue.enqueue(clip_path)
        return

    voice = client.voice_client_in(message.server)
    if voice is None:
        voice = await voicecomms.join(message, client)

    playing = True

    # Grab the file requested
    player = voice.create_ffmpeg_player(clip_path, after=_soundboard_finished)
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
    await client.send_message(message.channel, 'You will one day add mp3 links.')


def cleanup():
    # TODO ?
    return
