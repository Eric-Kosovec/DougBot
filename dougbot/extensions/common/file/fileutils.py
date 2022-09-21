import os
import shutil


async def find_file_async(start_path, filename):
    return find_file(start_path, filename)


def find_file(start_path, filename):
    wanted_name, wanted_extension = os.path.splitext(filename)

    wanted_name = wanted_name.strip()
    wanted_extension = wanted_extension.strip()

    for path, _, files in os.walk(start_path):
        for file in files:
            name, extension = os.path.splitext(file)
            if wanted_name.lower() == name.lower() and (len(wanted_extension) == 0 or wanted_extension.lower() == extension.lower()):
                return os.path.join(path, file)

    return None


def delete_directories(directory, ignore_errors=False, onerror=None):
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors, onerror)
