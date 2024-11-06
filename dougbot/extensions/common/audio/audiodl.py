from abc import ABC, abstractmethod


class AudioDL(ABC):
    """
    Basic structure for an audio downloader
    """

    @abstractmethod
    def info(self, url):
        """
        Get basic info about the url
        :param url: url of audio
        :return: dictionary of info
        """
        pass

    @abstractmethod
    def download(self, url, file_path):
        """
        Download audio from url to given file path
        :param url: url to download
        :param file_path: file path to be created and written to
        :return: list of dictionaries of audio info
        """
        pass

    @abstractmethod
    def _get_logger(self):
        """
        Gets a logger to log audio downloading to
        :return: logger
        """
        pass
