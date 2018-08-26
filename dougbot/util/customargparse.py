import argparse


class NoErrorMessageArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        self.exit(0, None)

    def exit(self, status=0, message=None):
        super(NoErrorMessageArgumentParser, self).exit(0, None)
