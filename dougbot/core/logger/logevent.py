
class LogEvent:

    def __init__(self):
        self._message = None
        self._exceptions = []

    def message(self, message):
        self._message = message
        return self

    def exception(self, exceptions):
        if isinstance(exceptions, list):
            self._exceptions.extend(exceptions)
        else:
            self._exceptions.append(exceptions)
        return self

    @staticmethod
    def error():
        pass
