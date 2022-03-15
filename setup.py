import subprocess


def update():
    with open('requirements.txt', 'r') as fd:
        for requirement in fd.readlines():
            if len(requirement.strip()) > 0:
                subprocess.run(['pip', 'install', '--upgrade', requirement.strip()])
                print()


if __name__ == '__main__':
    update()
