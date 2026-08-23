import re
from typing import Any

import yt_dlp
import yt_dlp.networking.impersonate
from yt_dlp import ImpersonateTarget

from dougbot import config
from dougbot.common.logger import Logger


class Ytdl:

    @classmethod
    def info(cls, url):
        normalized_url = cls._remove_playlist(url)
        ydl_opts = cls._setup_options()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                return ydl.extract_info(normalized_url, download=False, process=False)
            except Exception as e:
                Logger(__file__) \
                    .message('Failed to get url info') \
                    .add_field('url', url) \
                    .exception(e) \
                    .error()

                return {}


    @classmethod
    def download(cls, url, file_path, progress_hooks = None) -> bool:
        if progress_hooks:
            progress_hooks = progress_hooks if isinstance(progress_hooks, list) else [progress_hooks]

        normalized_url = cls._remove_playlist(url)
        ydl_opts = cls._setup_options(file_path, progress_hooks)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # TODO RETURN FILE PATH WITH EXTENSION?
            try:
                return ydl.download([normalized_url]) == 0
            except Exception as e:
                Logger(__file__) \
                    .message('Failed to download url') \
                    .add_field('url', url) \
                    .add_field('path', file_path) \
                    .exception(e) \
                    .error()

                return False


    @staticmethod
    def _setup_options(file=None, progress_hooks = None):
        configs = config.get_configuration()

        ydl_opts: dict[str, Any] = {
            'noplaylist': True, # Download single video instead of a playlist
            'nocheckcertificate': True, # Do not verify SSL certificates
            'quiet': True, # Do not print messages to stdout
            'no_warnings': True, # Do not print out anything for warnings
            'default_search': 'auto', # Prepend this string if an input url is not valid. 'auto' for elaborate guessing
            'source_address': '0.0.0.0', # Client-side IP address to bind to
            'socket_timeout': 60, # Time to wait for unresponsive hosts, in seconds
            'impersonate': ImpersonateTarget(client='firefox'),
            'geo_bypass': True,
            'js_runtimes': {
                'deno': {
                    'path': configs.deno_path
                }
            }
        }

        if file:
            # Dictionary of templates for output names. For compatibility with youtube-dl, a single string can be used
            ydl_opts['outtmpl'] = file
            ydl_opts['format'] = 'bestaudio/best' # Video format code
            ydl_opts['restrictfilenames'] = True # Do not allow "&" and spaces in file names
            ydl_opts['logger'] = Logger.logger()

            if progress_hooks:
                ydl_opts['progress_hooks'] = progress_hooks

        return ydl_opts


    @staticmethod
    def _remove_playlist(url):
        return re.sub(r'&list=[a-zA-Z0-9_-]+', '', url)
