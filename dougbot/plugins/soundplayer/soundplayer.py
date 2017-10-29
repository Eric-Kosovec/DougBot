import asyncio
import os

import discord

from dougbot.plugins.plugin import Plugin
from dougbot.plugins.soundplayer.track import Track
from dougbot.util.queue import Queue


class SoundPlayer(Plugin):

    _CLIPS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _CLIPS_DIR = os.path.join(_CLIPS_DIR, 'res', 'sbsounds')

    def __init__(self):
        super().__init__()
        self.sound_queue = Queue()
        self.playing = False
        self.paused = False
        self.player = None
        self.channel = None
        self.voice = None
        self.volume = 1.0

    @Plugin.command('join')
    async def join(self, event):
        # Don't join a channel if this was a private message.
        if event.channel().is_private:
            return

        user_voice_channel = event.message.author.voice.voice_channel

        # User is not in a voice channel.
        if not user_voice_channel:
            return

        # Check if already in a voice channel on the server
        if event.bot.voice_client_in(event.message.server):
            return

        # TODO FIND HOW TO GET RESULT WITHOUT NEEDING TO AWAIT/MAKE EVERYTHING ASYNCHRONOUS
        self.voice = await event.bot.join_voice_channel(user_voice_channel)

    @Plugin.command('leave')
    async def leave(self, event):
        # Don't leave if message is private
        if event.channel().is_private:
            return

        # User is not in a voice channel
        if not event.author().voice.voice_channel:
            return

        bot_voice_client = event.bot.voice_client_in(event.server())

        if not self._in_same_voice_channel(event):
            return

        self.voice = None
        self.playing = False

        await bot_voice_client.disconnect()

    @Plugin.command('sb', 'play', '<audio:str>')
    async def play(self, event, audio):
        track = Track(audio, self._CLIPS_DIR)

        self.sound_queue.enqueue(track)

        if self.playing:
            return

        # Join if need be
        if not self._in_voice_channel(event):
            await self.join(event)

        elif not self._in_same_voice_channel(event):
            return

        self._play_top_track()

    @Plugin.command('clips')
    async def clipslist(self, event):
        # List of clips can use
        #response = discord.Embed(color=0x8B0000, icon_url=event.bot.avatar_url)
        #response.set_author(name='A Sad Doug', icon_url=event.bot.avatar_url)
        #response.set_thumbnail(url=event.bot.avatar_url)

        clips = self._get_clipslist()

        i = 0
        msg = ''
        msg += ('-' * 60) + '\n'
        for clip in clips:
            msg += clip
            msg += ' ' * (40 - len(clip) * 2)
            i += 1
            if i == 3:
                msg += '\n'
                i = 0
        msg += 'a' + '\n'
        await event.reply(msg)
        #response.add_field(name='Sound Clips', value=msg)
        #response.set_footer(text='Play clip using command d!sb clipnamehere')
        #await event.reply(embed=response)

    def _get_clipslist(self):
        clips = []

        for file in os.listdir(self._CLIPS_DIR):
            if file.endswith('.mp3'):
                clips.append(file[:len(file) - len('.mp3')])

        return clips

    def _play_top_track(self):
        if self.playing or self.sound_queue.size() <= 0:
            return

        self.playing = True
        self.player = self._get_player(self.voice, self.sound_queue.dequeue())
        self.player.start()

    @Plugin.command('next', 'skip')
    async def skip(self, event):
        if self.playing and self.player:
            self.player.stop()
            self.playing = False
            self._play_top_track()

    @Plugin.command('resume')
    async def resume(self, event):
        if self.playing and self.player:
            self.player.resume()

    @Plugin.command('status')
    async def status(self, event):
        # TODO IS PLAYING/PAUSED/STOPPED
        return

    @Plugin.command('pause')
    async def pause(self, event):
        if self.playing and self.player:
            self.player.pause()
            self.paused = True

    @Plugin.command('stop', 'end')
    async def stop(self, event):
        if self.playing and self.player:
            self.player.stop()
            self.playing = False
            self.paused = False
            self.player = None
            self.sound_queue.clear()

    @Plugin.command('volume', '<new_volume:str>')
    async def volume(self, event, new_volume):
        # TODO MAKE SURE IT DOESN'T BREAK AND MAKE SURE YOU CAN DISPLAY THE SOUND INSTEAD OF SETTING
        new_volume = float(new_volume)
        if new_volume < 0.0:
            new_volume = 0.0
        elif new_volume > 200.0:
            new_volume = 200.0
        self.volume = new_volume / 100.0

        if self.playing and self.player:
            self.player.volume = self.volume

    def _soundplayer_finished(self):
        self.playing = False
        self._play_top_track()

    @staticmethod
    def _in_voice_channel(event):
        if not event:
            return False

        if event.bot.voice_client_in(event.server()):
            return True

        return False

    def _in_same_voice_channel(self, event):
        if not self._in_voice_channel(event):
            return False

        bot_vclient = event.bot.voice_client_in(event.server())

        if not event.author().voice:
            return False

        user_vchannel = event.author().voice.voice_channel

        if not user_vchannel:
            return False

        return bot_vclient.channel.id == user_vchannel.id

    def _get_player(self, vc, track):
        if not track.is_link:
            player = vc.create_ffmpeg_player(track.path, after=self._soundplayer_finished)
        else:
            player = vc.create_ytdl_player(track.audio, after=self._soundplayer_finished)
        #player.volume = self.volume
        return player
