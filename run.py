import sys

from dougbot.core.bot import DougBot

try:
    assert sys.version_info >= (3, 6)
except AssertionError:
    print('Fatal Error: DougBot supports only Python 3.6')
    exit(1)


def main():
    bot = DougBot('config/config.ini')
    bot.run()
    return


if __name__ == '__main__':
    main()
