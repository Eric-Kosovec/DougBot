import os
import subprocess

LINUX_PIP = 'pip3'
LINUX_PYTHON = 'python3'
WINDOWS_PIP = 'pip'
WINDOWS_PYTHON = 'python'


def update():
    with open('requirements.txt', 'r') as fd:
        for requirement in fd.readlines():
            clean_requirement = requirement.strip()
            if len(clean_requirement) > 1:
                if clean_requirement == 'pip':
                    commands = (f'{_python()} -m pip install --upgrade --force-reinstall '
                                f'{_pip_env_specific_arguments()} {clean_requirement}')
                else:
                    commands = (f'{_pip()} install --upgrade --force-reinstall '
                                f'{_pip_env_specific_arguments()} {clean_requirement}')

                subprocess.run(commands.split())
                print()


def _python():
    return WINDOWS_PYTHON if _is_windows() else LINUX_PYTHON


def _pip():
    return WINDOWS_PIP if _is_windows() else LINUX_PIP


def _pip_env_specific_arguments():
    return '' if _is_windows() else '--break-system-packages'


def _is_windows():
    return os.name == 'nt'


def _is_linux():
    return os.name == 'posix'


if __name__ == '__main__':
    update()
