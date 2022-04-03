from dougbot.common import limits

BLANK_DATA = '\u200b'


async def clear_fields(embed, field_count=limits.EMBED_FIELD_LIMIT):
    for _ in range(field_count):
        embed.add_field(name=BLANK_DATA, value=BLANK_DATA)
