ALIASES = ['sdt', 'theater', 'saddougtheater', 'cytube']

_SDT_LINK = 'https://cytu.be/r/SadDoug'

async def run(alias, message, args, client):
    await client.send_message(message.channel, _SDT_LINK)
