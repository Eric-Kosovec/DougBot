from dougbot.common import limits


def split_message(text, limit=limits.MESSAGE_CHARACTER_LIMIT):
    return [text[i:i + limit].strip() for i in range(0, len(text), limit)]


async def async_split_message(text, limit=limits.MESSAGE_CHARACTER_LIMIT):
    return split_message(text, limit)
