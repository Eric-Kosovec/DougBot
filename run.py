import sys

from dougbot.core.bot import DougBot

try:
    assert sys.version_info >= (3, 7)
except AssertionError:
    print('Fatal Error: DougBot supports only Python 3.7+', file=sys.stderr)
    exit(1)


def main():
    bot = DougBot('config/token', 'config/bot_config.ini', 'config/server_config.ini')
    bot.run()


if __name__ == '__main__':
    main()
