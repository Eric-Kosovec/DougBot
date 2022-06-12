import subprocess


def update():
    with open('requirements.txt', 'r') as fd:
        for requirement in fd.readlines():
            cleansed_requirement = requirement.strip()
            if len(cleansed_requirement) > 1:
                subprocess.run(['pip', 'install', '--upgrade', cleansed_requirement])
                print()


if __name__ == '__main__':
    update()
