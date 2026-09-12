import discord
from discord import Embed
from discord.ext import commands

from dougbot.common.logger import Logger
from dougbot.core.bot import DougBot
from dougbot.extensions.tarkov.tarkov_lib import TarkovLib

_EMBED_COLOR = 0x1fdec7


class TarkovCommands(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    async def price(self, ctx: commands.Context, *, item_name: str):
        try:
            item_results = await TarkovLib.get_items(item_name)
        except Exception as e:
            Logger(__file__).message("Failed to fetch Tarkov items").exception(e).error()
            await ctx.send("Something went wrong looking that item up. Try again later.")
            return

        if len(item_results) == 0:
            await ctx.send("No items found with that name.")
        elif len(item_results) > 25:
            await ctx.send("More than 25 results. Here are the first 25.", view=TarkovItem(item_results))
        else:
            await ctx.send("Here's what I got", view=TarkovItem(item_results))

    @commands.command()
    async def getItem(self, ctx: commands.Context, item_id: str):
        try:
            item_results = await TarkovLib.get_item(item_id)
        except Exception as e:
            Logger(__file__).message("Failed to fetch Tarkov item").exception(e).error()
            await ctx.send("Something went wrong looking that item up. Try again later.")
            return

        if item_results is None:
            await ctx.send("No item found with that id.")
            return

        await ctx.send(embed=_build_item_embed(item_results))


def _build_item_embed(item: dict) -> Embed:
    embed = Embed(title=item["name"], color=_EMBED_COLOR)
    if item.get("image8xLink"):
        embed.set_thumbnail(url=item["image8xLink"])
    for trader in item["sellFor"]:
        embed.add_field(name=trader["vendor"]["name"], value=trader["price"], inline=True)
    return embed


class TarkovItem(discord.ui.View):
    def __init__(self, item_list: list):
        super().__init__()
        for item in item_list[:25]:
            self.add_item(TarkovItemButton(item["name"], item["id"]))


class TarkovItemButton(discord.ui.Button['TarkovItem']):

    def __init__(self, label: str, item_id: str):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.item_id = item_id

    async def callback(self, interaction: discord.Interaction):
        try:
            item_results = await TarkovLib.get_item(self.item_id)
        except Exception as e:
            Logger(__file__).message("Failed to fetch Tarkov item").exception(e).error()
            await interaction.response.send_message("Something went wrong looking that item up.", ephemeral=True)
            return

        await interaction.response.send_message(embed=_build_item_embed(item_results))


def setup(bot):
    bot.add_cog(TarkovCommands(bot))