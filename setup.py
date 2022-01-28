import subprocess


def update():
    with open('requirements.txt', 'r') as req_file:
        for req in req_file:
            subprocess.run(['pip', 'install', '--upgrade', req.strip()])
            print()


if __name__ == '__main__':
    update()
