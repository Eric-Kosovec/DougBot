from pprint import pprint

from nextcord import Embed

from dougbot.common.limits import Limits


def split_embed(embed):
    # Length is combination of: Title (256), description (4096), field names (256)/field values (1024) at max of 25 pairs, footer text (2048)

    #if is_embed_sendable(embed):
    #    return [embed]

    base_embed_dict = embed.to_dict()
    nonstatic_fields = _strip_nonstatic_fields(base_embed_dict)

    title = nonstatic_fields

    pprint(base_embed_dict)
    print()
    pprint(nonstatic_fields)
    print()
    for field in nonstatic_fields:
        print(field)

    split_embeds = []


def _create_embed(static_fields, dynamic_fields):
    embed_dict = static_fields.copy()
    length = _embed_length(embed_dict)





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


def is_embed_sendable(embed):
    return len(embed) <= Limits.EMBED_CHARACTER_LIMIT


def _strip_nonstatic_fields(embed_dict):
    nonstatic_field_titles = [
        'title',
        'description',
        'fields',
        'footer'
    ]
    return [{t: embed_dict.pop(t)} for t in nonstatic_field_titles if t in embed_dict]


def _testing_embed():
    embed = Embed(title="Title", url="https://cog-creators.github.io/discord-embed-sandbox/", description="Description", color=0xff0000)
    embed.set_author(name="Author name")
    embed.add_field(name="Field Name", value="Field Value", inline=False)
    embed.set_footer(text="Footer")
    return embed


if __name__ == '__main__':
    split_embed(_testing_embed())
