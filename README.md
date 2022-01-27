# DougBot
Discord bot for the SadDoug guild.

## Running/Development

#### OS Independent
* Install Python latest Python. While installing, check the button add Python to PATH variable.
* Run `setup.py` from the console through the command `python3 setup.py`.
* Under the `config` directory, create your own token file called `token` containing solely the token given to you from Discord for your registered bot, then change the `config.ini` file to suit your needs, and `dougbot/core/config.py`, if need be.
* To start the bot, execute `run.bat` or from the console through the command `python3 run.py`.

#### Windows
* Install Python version 3.8 (higher is not supported). While installing, check the button add Python to PATH variable.
* Put the folder `DougBot/bin` into your PATH variable and restart your machine.

#### Linux

## Installing/Updating Required Libraries
Run `setup.py` from the console through the command `python3 setup.py`.

## Extension Development
Skeleton extension, `skeleton.py`, in `dougbot/extensions/example` can be used as the basis for any new extension, changing the class name accordingly.

Note: The setup function is required for a file containing extensions and is meant to register the extension classes to the bot. All extension classes must subclass `commands.Cog`.

### Resources
The `resources` folder should mirror the source code structure. Therefore, resources for an extension should go within a folder with the same name as its package; e.g. music extension 