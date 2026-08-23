import asyncio

from discord import Message
from discord.ext.commands import Context


class Track:

    def __init__(self, source, generation, ctx: Context):
        self.source = source
        self.source_path = None
        self.generation = generation
        self.ctx: Context = ctx
        self.exception = None
        self.video_info: dict | None = None
        self.progress_message: Message | None = None
        self.ready = asyncio.Event()
