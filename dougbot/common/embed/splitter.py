from pprint import pprint

from nextcord import Embed

from dougbot.common.limits import Limits


def split_embed(embed):
    # Length is combination of: Title (256), description (4096), field names (256)/field values (1024) at max of 25 pairs, footer text (2048)

    #if is_embed_sendable(embed):
    #    return [embed]

    base_embed_dict = embed.to_dict()
    dynamic_fields = _strip_nonstatic_fields(base_embed_dict)

    base_embed_dict['title'] = _ellipsis(base_embed_dict['title'], Limits.EMBED_TITLE_LIMIT)
    footer = _ellipsis(dynamic_fields['footer'], Limits.EMBED_FOOTER_TEXT_LIMIT)

    # Description split across multiple
    description = dynamic_fields['description']
    max_length = Limits.EMBED_DESCRIPTION_LIMIT
    descriptions = [description[i:i + max_length] for i in range(0, len(description), max_length)]

    for description in descriptions:
        pass

    # Fields across multiple
    # Footer only on first

    pprint(base_embed_dict)
    print()
    pprint(dynamic_fields)

    split_embeds = []


def _create_embed(static_fields, description=None, fields=None, footer=None):
    embed = Embed.from_dict(static_fields)

    if description is not None:
        embed.description = description

    if footer is not None:
        embed.set_footer(**footer)

    if fields is not None:
        while _is_embed_sendable(embed):
            if len(fields) == 0:
                return embed
            embed.add_field(**fields[0])
            fields.pop(0)

        fields.insert(0, embed.fields[-1])
        embed.remove_field(-1)

    return embed


def _ellipsis(text, max_length):
    if len(text) <= max_length:
        return text
    return f'{text[:max_length - 3]}...'


def _embed_length(embed_dict):
    length = 0
    for key, value in embed_dict.items():
        if key == 'fields':
            for field in value:
                length += len(field['name']) + len(field['value'])
        elif key == 'footer':
            length += len(value['text'])
        elif key in ['description', 'title']:
            length += len(value)
    return length


def _is_embed_sendable(embed):
    return len(embed) <= Limits.EMBED_CHARACTER_LIMIT


def _strip_nonstatic_fields(embed_dict):
    nonstatic_field_titles = [
        'description',
        'fields',
        'footer'
    ]
    return {t: embed_dict.pop(t) for t in nonstatic_field_titles if t in embed_dict}


def _testing_embed():
    embed = Embed(title="Title", url="https://cog-creators.github.io/discord-embed-sandbox/", description="Description", color=0xff0000)
    embed.set_author(name="Author name")
    embed.add_field(name="Field Name", value="Field Value", inline=False)
    embed.set_footer(text="Footer")
    return embed


if __name__ == '__main__':
    split_embed(_testing_embed())
