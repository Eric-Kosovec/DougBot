from Lib import random


async def run(alias, message, args, client):
    if len(args) == 0:
        await client.send_message(message.channel, '%f' % random.random())
        return

    if len(args) < 2:
        await client.confusion(message)
        return

    lower_bound = args[0]
    upper_bound = args[1]

    if '.' in lower_bound or '.' in upper_bound:
        delta = 0.1
        lower_bound = float(lower_bound)
        upper_bound = float(upper_bound)

        if lower_bound > upper_bound:
            tmp = lower_bound
            lower_bound = upper_bound
            upper_bound = tmp

        bound_range = upper_bound + delta - lower_bound
        rand_float = random.random() * bound_range + lower_bound

        if rand_float > upper_bound:
            rand_float = upper_bound

        await client.send_message(message.channel, '%f' % rand_float)
    else:
        lower_bound = int(lower_bound)
        upper_bound = int(upper_bound)

        if lower_bound > upper_bound:
            tmp = lower_bound
            lower_bound = upper_bound
            upper_bound = tmp

        await client.send_message(message.channel, '%d' % random.randint(lower_bound, upper_bound))
