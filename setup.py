import subprocess


def update():
    with open('requirements.txt', 'r') as fd:
        for requirement in fd.readlines():
            clean_requirement = requirement.strip()
            if len(clean_requirement) > 1:
                if clean_requirement == 'pip':
                    commands = ['python', '-m', 'pip', 'install', '--upgrade', '--force-reinstall', clean_requirement]
                else:
                    commands = ['pip', 'install', '--upgrade', '--force-reinstall', clean_requirement]

                subprocess.run(commands)
                print()


if __name__ == '__main__':
    update()
