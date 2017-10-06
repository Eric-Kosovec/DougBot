import subprocess

ALIASES = ['github', 'gitsounds']


async def run(alias, message, args, client):
    if alias == 'gitsounds':
        await _git_command()
        return
    elif alias == 'github':
        await client.send_message(message.channel, client.config.source_code)


async def _git_command():
    # TODO FIX
    subprocess.run(['git', 'fetch'])
    subprocess.run(['git', 'checkout', 'HEAD', 'resources'])
