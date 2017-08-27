from Lib import random

trumps = ["rock", "scissors", "paper", "rock"]

async def run(alias, message, args, client):
    if len(args) <= 0:
        await help(alias, message, args, client)
        return

    their_move = args[0].lower()
    our_move = trumps[_random_move(len(trumps) - 1)]

    if their_move not in trumps:
        await client.add_reaction(message, "❓")
        return

    if their_move == our_move:
        await client.send_message(message.channel, "%s\nIt's a tie!" % our_move.title())
    elif trumps[trumps.index(their_move) + 1] == our_move:
        await client.send_message(message.channel, "%s\nYou won." % our_move.title())
    else:
        await client.send_message(message.channel, "%s\nI won." % our_move.title())


def _random_move(max_val):
    return random.randint(0, max_val)


async def help(alias, message, args, client):
    await client.send_message(message.channel, "rps command format: d!rps [play], where [play] is replaced by one of: rock, paper, scissors.")
    return