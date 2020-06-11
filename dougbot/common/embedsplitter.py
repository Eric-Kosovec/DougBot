import datetime

import discord
from discord import Embed

from dougbot.common.limits import *


def split_embed(embed):
    current_embed = embed
    split_embeds = [current_embed]

    embed_standard = {'thumbnail': embed.thumbnail, 'color': embed.color, 'timestamp': embed.timestamp,
                      'image': embed.image, 'author': embed.author, 'footer': embed.footer}

    if len(embed.title) > EMBED_TITLE_LIMIT:
        embed.title = f'{embed.title[:EMBED_TITLE_LIMIT - 3]}...'
    running_size = len(embed.title)

    if len(embed.description) > EMBED_DESCRIPTION_LIMIT:
        pass

    return split_embeds


def _create_embed():
    embed = Embed(title="title ~~(did you know you can have markdown here too?)~~",
                          colour=discord.Colour(0xd25748), url="https://discordapp.com",
                          description="this supports [named links](https://discordapp.com) on top of the previously shown subset of markdown. ```\nyes, even code blocks```",
                          timestamp=datetime.datetime.utcfromtimestamp(1590820730))

    embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_author(name="author name", url="https://discordapp.com",
                     icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
    embed.set_footer(text="footer text", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")

    embed.add_field(name="🤔", value="some of these properties have certain limits...")
    embed.add_field(name="😱", value="try exceeding some of them!")
    embed.add_field(name="🙄",
                    value="an informative error should show up, and this view will remain as-is until all issues are fixed")
    embed.add_field(name="<:thonkang:219069250692841473>", value="these last two", inline=True)
    embed.add_field(name="<:thonkang:219069250692841473>", value="are inline fields", inline=True)
    return embed


print(_create_embed().to_dict())