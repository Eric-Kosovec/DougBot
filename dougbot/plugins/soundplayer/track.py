import os

from dougbot.core.command import CommandError


class Track:

    def __init__(self, audio, clip_base):
        self.audio = audio
        self.is_link = self._is_link(audio)
        self.path = None

        if not self.is_link:
            self.path = self._create_path(audio, clip_base)

            try:
                with open(self.path, 'r'):
                    pass
            except IOError:
                raise CommandError(f'Track {audio} does not exist')

    @staticmethod
    def _create_path(audio, clip_base):
        for directory in os.listdir(clip_base):
            if '.' not in directory:
                if f'{audio}.mp3' in os.listdir(os.path.join(clip_base, directory)):
                    return os.path.join(clip_base, directory, f'{audio}.mp3')
        return None

    @staticmethod
    def _is_link(audio):
        link = False

        if not audio:
            return link

        if audio.startswith('https://') or audio.startswith('http://') or audio.startswith('www.'):
            link = True

        return link
