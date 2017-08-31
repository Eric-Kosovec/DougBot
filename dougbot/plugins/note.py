notes = dict()


async def run(alias, message, args, client):
    if len(args) <= 0:
        await client.add_reaction(message, "❓")
        return

    command = args[0]

    if command == "clear":
        await _note_clear(message, client)
    elif command == "size":
        await _note_size(message, client)

    # TODO GATHER INTO KEY/VALUE IF NEEDED

    return


async def _note_add(key, value, message, client):
    notes[key] = value
    await client.send_message(message.channel, "Added to notes.")


async def _note_remove(key, message, client):
    value = None

    try:
        value = notes[key]
        del notes[key]
    except KeyError:
        value = "Key %s not found." % key
    finally:
        await client.send_message(message.channel, value)


async def _note_get(key, message, client):
    value = ""
    try:
        value = notes[key]
    except KeyError:
        value = "Key %s not found." % key
    finally:
        await client.send_message(message.channel, value)


async def _note_clear(message, client):
    notes.clear()
    await client.send_message(message.channel, "Notes cleared.")


async def _note_size(message, client):
    await client.send_message(message.channel, "%d" % len(notes))
