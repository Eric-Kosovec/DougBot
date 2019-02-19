import sys

from update_deps import update

try:
    assert sys.version_info >= (3, 6)
except AssertionError:
    print('Fatal Error: DougBot supports only Python 3.6+')
    exit(1)

if __name__ == '__main__':
    update()
