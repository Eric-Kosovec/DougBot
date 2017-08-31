ALIASES = ["github", "git"]


async def run(alias, message, args, client):
    await client.send_message(message.channel, client.config.source_code)
