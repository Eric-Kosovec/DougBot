# Define if you want multiple commands to route to here. Be careful not to use the same command as a different plugin.
# NOTE: Must be ALIASES in all caps, and must be list of strings of command names.
# If you have no aliases, then you can ignore the alias parameter of the run and help functions. In this case, it would
# be the module name.
ALIASES = []


async def run(alias, message, args, client):
    # Do stuff here
    return


async def help(alias, message, args, client):
    # Send message through client to message channel about command usage
    return


async def cleanup(client):
    return
