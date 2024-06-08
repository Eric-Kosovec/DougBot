import sys

from dougbot.core.bot import DougBot

try:
    assert sys.version_info >= (3, 10)
except AssertionError:
    print('Fatal: DougBot supports only Python 3.10+', file=sys.stderr)
    exit(1)


def main():
    DougBot().run()


if __name__ == '__main__':
    main()
