# DougBot
Python-based Discord bot for the SadDoug server.

## Running/Development

#### OS Independent
* Install the latest Python; while installing, check the button add Python to PATH variable.
* Setup environment variable called `DOUGBOT_TOKEN` with the bot's token and restart (if on Windows, see section below before restarting).
* Run `setup.py` through the command `python3 setup.py`.
* Change the `resources/config/config.ini` file to suit your needs, and `dougbot/config.py`, if need be.
* For a development environment, create `resources/config/dev_config.ini`. Any settings in this file will override the main config file.
* To start the bot, run `run.py`.

#### Windows
* Download FFmpeg and place somewhere on your machine. Add directory containing `ffmpeg.exe` to PATH variable and restart.

#### Linux
* TODO

## Installing/Updating Required Libraries
Run `setup.py` using the command `python3 setup.py`.

## Extension Development
Skeleton extension, `example.py`, in `dougbot/extensions/example` can be used as the basis for any new extension, changing the class name accordingly.

Note: The `setup` function is required for a file containing extensions and is meant to register the extension classes to the bot. The `teardown` function is not required, but is for cleanup and is called after the bot stops or calls `remove_cog`.
All extension classes must subclass `commands.Cog`.

### Resources
The `resources/dougbot` folder should mirror the source code structure. Therefore, resources for an extension should go within a folder with the same name as its package; e.g., music extension: `resources/dougbot/extensions/music`.
