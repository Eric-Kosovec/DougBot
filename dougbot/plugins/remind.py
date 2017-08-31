import asyncio


async def run(alias, message, args, client):
    if len(args) <= 1:
        return

    seconds = int(args[0])
    print(seconds)
    if seconds <= 0:
        # TODO PRINT MESSAGE RIGHT AWAY
        return

    remind_of = ""

    for i in range(1, len(args)):
        remind_of += args[i] + " "

    await remind_send_reminder(seconds, remind_of, client, message.channel)


async def remind_send_reminder(seconds, remind_of, client, channel):
    await asyncio.sleep(seconds)
    # TODO MAKE MORE OBVIOUS AND MAYBE ONLY SEND TO USER IF IT WAS A PRIVATE MESSAGE
    await client.send_message(channel, remind_of)
