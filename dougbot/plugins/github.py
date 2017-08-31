import subprocess

ALIASES = ["github", "gitsounds"]


async def run(alias, message, args, client):
    if alias == "gitsounds":
        await _git_command()

    await client.send_message(message.channel, client.config.source_code)


def _git_command():
    subprocess.run(["git", "fetch"])
    subprocess.run(["git", "checkout", "HEAD", "..\\resources"])
    return
