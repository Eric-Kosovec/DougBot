import subprocess
import sys

try:
    assert sys.version_info >= (3, 7)
except AssertionError:
    print('Fatal Error: DougBot supports only Python 3.7+', file=sys.stderr)
    exit(1)


def update():
    # Using 'with' allows for file to close when done, even with exceptions.
    with open('requirements.txt', 'r') as req_file:
        for req in req_file:
            subprocess.run(['pip', 'install', '--upgrade', req.strip()])
            print()


if __name__ == '__main__':
    update()
