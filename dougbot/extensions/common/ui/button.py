from discord import Interaction
from discord.ui.button import Button


class DougButton(Button):

    def __init__(self, *, callback=None, **kwargs):
        super().__init__(**kwargs)
        self._callback = callback

    async def callback(self, interaction: Interaction):
        if self._callback:
            await self._callback(interaction)
