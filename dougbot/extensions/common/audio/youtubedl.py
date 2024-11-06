import sys

import youtube_dl

from dougbot.extensions.common.audio.audiodl import AudioDL


class YouTubeDL(AudioDL):

    _FILE_OPTION = 'outtmpl'
    _LOGGER_OPTION = 'logger'
    _PROGRESS_HOOKS_OPTION = 'progress_hooks'

    def __init__(self, progress_hooks=None, logger=None):
        self._progress_hooks = None

        if progress_hooks:
            self._progress_hooks = progress_hooks if isinstance(progress_hooks, list) else [progress_hooks]

        self._logger = logger

    def info(self, url):
        ytdl = youtube_dl.YoutubeDL(self._setup_options(url))
        return ytdl.extract_info(url, False)

    def download(self, url, file_path):
        ytdl = youtube_dl.YoutubeDL(self._setup_options(file_path))
        return ytdl.extract_info(url)

    def _get_logger(self):
        return self._logger

    def _setup_options(self, file=None):
        opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'opus',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }

        if file:
            opts[self._FILE_OPTION] = file

        if self._progress_hooks:
            opts[self._PROGRESS_HOOKS_OPTION] = self._progress_hooks if isinstance(self._progress_hooks, list) \
                else [self._progress_hooks]

        logger = self._get_logger()
        if logger:
            opts[self._LOGGER_OPTION] = logger

        return opts
