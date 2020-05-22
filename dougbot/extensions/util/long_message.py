import string

import dougbot.common.limits as limits


def is_long_message(message, limit=limits.MESSAGE_CHARACTER_LIMIT):
    if message is None or type(message) != str:
        return False
    return len(message) > limit


def columnize(message):
    return


def long_message(message, limit=limits.MESSAGE_CHARACTER_LIMIT):
    if not is_long_message(message, limit):
        return [message]

    shorter_messages = []

    window_min = 0
    window_max = limit - 1

    while window_min < len(message) and window_max < len(message):
        # Move to a non-whitespace for start of message
        while window_min < len(message) and message[window_min] in string.whitespace:
            window_min += 1
            window_max += 1
        if window_min >= len(message):
            break
        if window_max >= len(message):
            window_max = len(message) - 1

        # Window ends in middle of word, so go back to the last whitespace, if it exists
        if window_max + 1 < len(message) and message[window_max + 1] not in string.whitespace:
            i = window_max
            while i > window_min and message[i] not in string.whitespace:
                i -= 1
            if i > window_min:
                window_max = i
            shorter_messages.append(message[window_min:window_max + 1].strip())
        # Window ends at end of word
        else:
            clean_message = message[window_min:window_max + 1].strip()
            if len(clean_message) > 0:
                shorter_messages.append(clean_message)
        window_min = window_max + 1
        window_max = window_min + limit - 1

    if window_min < len(message) <= window_max:
        shorter_messages.append(message[window_min:len(message)].strip())

    return shorter_messages
