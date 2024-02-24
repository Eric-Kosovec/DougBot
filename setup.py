import getpass
import os
import subprocess
import sys

from dougbot import config

DOUGBOT_RUN_PY_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run.py')
DOUGBOT_SERVICE_UNIT = '''
[Unit]
Description=DougBot
After=network.target network-online.target

[Service]
Type=simple
User={username}
Group={group_name}
Restart=always
Environment="DOUGBOT_TOKEN={token}"
PermissionsStartOnly=true
ExecStartPre=/bin/mkdir -p /var/run/dougbot
PIDFile=/var/run/dougbot/service.pid
ExecStart=/usr/bin/python3 {run_py_path}

[Install]
WantedBy=multi-user.target
'''
DOUGBOT_UNIT_FILE_PATH = '/lib/systemd/system/dougbot.service'
DOUGBOT_WINDOWS_START_SCRIPT = (f'C:\\Users\\{getpass.getuser()}\\AppData\\Roaming'
                                f'\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\start_dougbot.bat')
IS_LINUX = os.name == 'posix'
IS_WINDOWS = os.name == 'nt'
LINUX_PIP = 'pip3'
LINUX_PYTHON = 'python3'
WINDOWS_PIP = 'pip'
WINDOWS_PYTHON = 'python'


def _install_dependencies():
    with open('requirements.txt', 'r') as fd:
        for requirement in fd.readlines():
            clean_requirement = requirement.strip()
            if len(clean_requirement) > 1:
                if clean_requirement == 'pip':
                    commands = (f'{_python()} -m pip install --upgrade --force-reinstall '
                                f'{_pip_arguments()} {clean_requirement}')
                else:
                    commands = (f'{_pip()} install --upgrade --force-reinstall '
                                f'{_pip_arguments()} {clean_requirement}')

                subprocess.run(commands.split())
                print()


def _add_persistence():
    if config.get_configuration().is_dev_bot:
        return

    if IS_WINDOWS:
        _start_on_windows_login()
    elif IS_LINUX:
        _create_linux_service()


def _remove_persistence():
    if IS_WINDOWS:
        _remove_from_windows_login()
    elif IS_LINUX:
        _remove_linux_service()


def _create_linux_service():
    if os.path.exists(DOUGBOT_UNIT_FILE_PATH):
        return

    if os.geteuid() != 0:
        raise PermissionError()

    username = getpass.getuser()
    dougbot_unit = DOUGBOT_SERVICE_UNIT.format(
        username=username,
        group_name=username,
        token=config.get_configuration().token,
        run_py_path=DOUGBOT_RUN_PY_PATH)

    with open(DOUGBOT_UNIT_FILE_PATH, 'w+') as service_file:
        service_file.write(dougbot_unit)

    subprocess.run('sudo systemctl daemon-reload'.split())
    subprocess.run('sudo systemctl enable dougbot.service'.split())


def _remove_linux_service():
    if not os.path.exists(DOUGBOT_UNIT_FILE_PATH):
        return

    if os.geteuid() != 0:
        raise PermissionError()

    os.remove(DOUGBOT_UNIT_FILE_PATH)


def _start_on_windows_login():
    if os.path.exists(DOUGBOT_WINDOWS_START_SCRIPT):
        return

    with open(DOUGBOT_WINDOWS_START_SCRIPT, 'w+') as batch_file:
        batch_file.write(f'call {WINDOWS_PYTHON} {DOUGBOT_RUN_PY_PATH}')


def _remove_from_windows_login():
    if os.path.exists(DOUGBOT_WINDOWS_START_SCRIPT):
        os.remove(DOUGBOT_WINDOWS_START_SCRIPT)


def _pip():
    return WINDOWS_PIP if IS_WINDOWS else LINUX_PIP


def _python():
    return WINDOWS_PYTHON if IS_WINDOWS else LINUX_PYTHON


def _pip_arguments():
    return '' if IS_WINDOWS else '--break-system-packages'


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--persist':
        try:
            _add_persistence()
        except PermissionError:
            print(f"Error: '{_python()} setup.py --persist' must be run with 'sudo -E'", file=sys.stderr)
    elif len(sys.argv) == 2 and sys.argv[1] == '--remove-persist':
        try:
            _remove_persistence()
        except PermissionError:
            print(f"Error: '{_python()} setup.py --remove-persist' must be run with 'sudo'", file=sys.stderr)
    else:
        _install_dependencies()
