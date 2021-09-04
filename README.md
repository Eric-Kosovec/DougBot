# DougBot
Discord bot for the SadDoug guild.

## Running/Development
#### Windows
* Install Python version 3.7 or higher. While installing, check the button add Python to PATH variable.
* Put the folder `DougBot/bin` into your PATH variable and restart your machine.
* Run `setup.py` from the console through the command `python setup.py`.
* Under the `config` directory, create your own token file called `token` containing solely the token given to you from Discord for your registered bot, then change the `config.ini` file to suit your needs, and `dougbot/core/config.py`, if need be.
* To start the bot, execute `run.bat` or from the console through the command `python run.py`.

## Installing/Updating Required Libraries
Run `setup.py` from the console through the command `python setup.py`.

## Extension Development
Skeleton extension in `dougbot/extensions/example`. `Skeleton.py` can be used as the basis for any new extension, changing the class name accordingly. 

Note: The setup function is required for a file containing extensions and is meant to register the extension classes to the bot. All extension classes must subclass `commands.Cog`.
