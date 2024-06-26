import getpass
import os
import subprocess
import sys

from dougbot import config

IS_LINUX = os.name == 'posix'
IS_WINDOWS = os.name == 'nt'
LINUX_PIP = 'pip3'
LINUX_PYTHON = 'python3'
RUN_PY_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run.py')

SERVICE_UNIT = '''
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

UNIT_FILE_PATH = '/lib/systemd/system/dougbot.service'
WINDOWS_PIP = 'pip'
WINDOWS_PYTHON = 'python'
WINDOWS_START_SCRIPT = (f'C:\\Users\\{getpass.getuser()}\\AppData\\Roaming'
                        f'\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\start_dougbot.bat')


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

    ffmpeg_exception = None if IS_WINDOWS else _install_ffmpeg()
    if ffmpeg_exception:
        print(f'\nFFmpeg not installed: {ffmpeg_exception}', file=sys.stderr)
    elif IS_LINUX:
        print(f'FFmpeg installed')


def _install_ffmpeg():
    try:
        result = subprocess.run('which ffmpeg'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # ffmpeg installed
        if result.returncode == 0:
            return None

        # Update the package list
        subprocess.run('sudo apt-get update'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Install ffmpeg
        subprocess.run('sudo apt-get install -y ffmpeg'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, check=True)

        return None
    except Exception as e:
        return e


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
    if os.path.exists(UNIT_FILE_PATH):
        return

    if os.geteuid() != 0:
        raise PermissionError()

    username = getpass.getuser()
    dougbot_unit = SERVICE_UNIT.format(
        username=username,
        group_name=username,
        token=config.get_configuration().token,
        run_py_path=RUN_PY_PATH)

    with open(UNIT_FILE_PATH, 'w+') as service_file:
        service_file.write(dougbot_unit)

    subprocess.run('sudo systemctl daemon-reload'.split())
    subprocess.run('sudo systemctl enable dougbot.service'.split())


def _remove_linux_service():
    if not os.path.exists(UNIT_FILE_PATH):
        return

    if os.geteuid() != 0:
        raise PermissionError()

    os.remove(UNIT_FILE_PATH)


def _start_on_windows_login():
    if os.path.exists(WINDOWS_START_SCRIPT):
        return

    with open(WINDOWS_START_SCRIPT, 'w+') as batch_file:
        batch_file.write(f'call {WINDOWS_PYTHON} {RUN_PY_PATH}')


def _remove_from_windows_login():
    if os.path.exists(WINDOWS_START_SCRIPT):
        os.remove(WINDOWS_START_SCRIPT)


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
