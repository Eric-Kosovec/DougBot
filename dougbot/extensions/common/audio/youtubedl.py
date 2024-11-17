import yt_dlp

from dougbot.common.logger import Logger
from dougbot.extensions.common.audio.audiodl import AudioDL
from dougbot.extensions.common.audio.util import ytutil


class YouTubeDL(AudioDL):

    _FILE_OPTION = 'outtmpl'
    _LOGGER_OPTION = 'logger'
    _PROGRESS_HOOKS_OPTION = 'progress_hooks'

    def __init__(self, progress_hooks=None, logger: Logger = None):
        self._progress_hooks = None

        if progress_hooks:
            self._progress_hooks = progress_hooks if isinstance(progress_hooks, list) else [progress_hooks]

        self._logger = logger

    def info(self, url):
        normalized_url = ytutil.remove_playlist(url)
        ydl_opts = self._setup_options()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                return ydl.extract_info(normalized_url, download=False, process=False)
            except Exception as e:
                self._logger.message('Failed to get url info') \
                    .add_field('url', url) \
                    .exception(e) \
                    .error()
                return {}

    def download(self, url, file_path):
        normalized_url = ytutil.remove_playlist(url)
        ydl_opts = self._setup_options(file_path)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # TODO RETURN FILE PATH WITH EXTENSION?
            try:
                return ydl.download([normalized_url])
            except Exception as e:
                self._logger.message('Failed to download url') \
                    .add_field('url', url) \
                    .add_field('path', file_path) \
                    .exception(e) \
                    .error()
                return 1

    def _get_logger(self):
        return self._logger

    def _setup_options(self, file=None):
        ydl_opts = {
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
            ydl_opts[self._FILE_OPTION] = file
            ydl_opts['format'] = 'm4a/bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
            ydl_opts['restrictfilenames'] = True

            if self._progress_hooks:
                ydl_opts[self._PROGRESS_HOOKS_OPTION] = self._progress_hooks if isinstance(self._progress_hooks, list) \
                    else [self._progress_hooks]

        logger = self._get_logger()
        if logger:
            ydl_opts[self._LOGGER_OPTION] = logger

        return ydl_opts
