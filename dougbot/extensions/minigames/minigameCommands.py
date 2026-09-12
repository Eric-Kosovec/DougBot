# Chat minigames for DougBot.
import asyncio
import math
import random
from contextlib import suppress

import discord
from discord import Embed
from discord.ext import commands

from dougbot.common.logger import Logger
from dougbot.core.bot import DougBot
from dougbot.extensions.minigames.emoji_racers import EMOJI_RACERS, EmojiRacer
from dougbot.extensions.minigames.minigameLib import EmojiRacerStore

_RACE_COLOR = 0x228B22
_SLOTS_COLOR = 0xA2AFB8

_JOIN_EMOJI = "<:smug32:255496009361129483>"
_SCARED_EMOJI = "<:sipsScared:819393684549533716>"

_JOIN_WINDOW_SECS = 15
_ROUND_PAUSE_SECS = 2
_MIN_RACERS = 4
_TRACK_LENGTH = 10
# After this many rounds the whole field gets a growing chance/speed bonus so
# stalled races still finish.
_OVERTIME_ROUND = 20

_FILLER_NAMES = (
    "Shot Hottie", "Anonymous", "( ͡° ͜ʖ ͡°)", "TryhardTimmy", "Doug", "Cool Whip",
    "Thunder Bunt", "Lowercase Guy", "✧GͥOͣDͫ✧", "𝐅𝐎𝐑𝐓𝐍𝐈𝐓𝐄 GOD", "¯\\_(ツ)_/¯",
)

_SLOT_EMOJIS = (
    "<:sipsScared:819393684549533716>", "<:passMan:256140704806338560>",
    "<:fireball:267121761173110784>", "<:gabeN:255489512543748097>",
    "<:doug:337020649753018368>", "<:ripley:532377971009257492>",
    "<:alex:338163624063533056>",
)


class _Racer:
    """A competitor's live state during a single race."""

    __slots__ = ("name", "mention", "card", "position")

    def __init__(self, competitor, card: EmojiRacer):
        if isinstance(competitor, str):
            self.name = self.mention = competitor
        else:
            self.name = competitor.display_name
            self.mention = competitor.mention
        self.card = card
        self.position = 1.0


class MinigameCommands(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        self._stats = EmojiRacerStore()
        # Channel ids with a race in progress - one race per channel at a time.
        self._racing_channels: set[int] = set()

    # --------------------race------------------------------------------------

    @commands.command(aliases=["race"])
    async def startrace(self, ctx: commands.Context):
        """Start an emoji drag race in this channel."""
        if ctx.channel.id in self._racing_channels:
            await ctx.message.add_reaction(_SCARED_EMOJI)
            return

        self._racing_channels.add(ctx.channel.id)
        try:
            message = await ctx.send("The Depression races are starting!")
            competitors = await self._sign_up(ctx, message)
            racers, winner = await self._run_race(message, competitors)
            await self._save_result(ctx, racers, winner)
        except Exception as e:
            Logger(__file__).message("Emoji race failed").context(ctx).exception(e).error()
        finally:
            self._racing_channels.discard(ctx.channel.id)
            with suppress(discord.HTTPException):
                await ctx.message.delete()

    async def _sign_up(self, ctx: commands.Context, message: discord.Message) -> list:
        """Run the sign-up countdown and return the competitor list."""
        await message.add_reaction(_JOIN_EMOJI)

        for remaining in range(_JOIN_WINDOW_SECS, 0, -1):
            await message.edit(
                content=f"The Depression races start in {remaining}s - "
                        f"react with {_JOIN_EMOJI} to enter!"
            )
            await asyncio.sleep(1)

        await message.edit(content="Let the sadness begin. Setting up the race...")
        competitors = await self._joined_members(ctx, message)
        with suppress(discord.HTTPException):
            await message.clear_reactions()

        shortfall = _MIN_RACERS - len(competitors)
        if shortfall > 0:
            competitors.extend(random.sample(_FILLER_NAMES, shortfall))
        return competitors

    @staticmethod
    async def _joined_members(ctx: commands.Context, message: discord.Message) -> list:
        message = await ctx.fetch_message(message.id)

        members: list = []
        for reaction in message.reactions:
            if str(reaction.emoji) != _JOIN_EMOJI:
                continue
            async for user in reaction.users():
                if not user.bot and user not in members:
                    members.append(user)
        return members

    async def _run_race(self, message: discord.Message, competitors: list) -> tuple[list[_Racer], _Racer]:
        cards = self._deal_cards(len(competitors))
        racers = [_Racer(c, card) for c, card in zip(competitors, cards)]
        field_chance, field_speed = self._field_modifiers(cards)

        round_no = 0
        winner: _Racer | None = None
        await self._render(message, racers, round_no, field_chance, field_speed)

        while winner is None:
            round_no += 1
            await asyncio.sleep(_ROUND_PAUSE_SECS)

            catchup = max(0, round_no - _OVERTIME_ROUND)
            chance, speed = field_chance + catchup, field_speed + catchup

            for racer in racers:
                racer.position += self._advance(racer.card, chance, speed)
                if racer.position >= _TRACK_LENGTH and winner is None:
                    racer.position = _TRACK_LENGTH
                    winner = racer

            await self._render(message, racers, round_no, chance, speed)

        await message.edit(
            content=f"🏆 Winner: {winner.mention}\n{winner.card.emoji} {winner.card.quote}",
            embed=None,
        )
        return racers, winner

    @staticmethod
    def _deal_cards(count: int) -> list[EmojiRacer]:
        if count <= len(EMOJI_RACERS):
            return random.sample(EMOJI_RACERS, count)
        return random.choices(EMOJI_RACERS, k=count)

    @staticmethod
    def _field_modifiers(cards: list[EmojiRacer]) -> tuple[float, float]:
        if any(card.protection for card in cards):
            return 0.0, 0.0
        return (
            sum(card.field_chance_effect for card in cards),
            sum(card.field_speed_effect for card in cards),
        )

    @staticmethod
    def _advance(card: EmojiRacer, field_chance: float, field_speed: float) -> float:
        chance = max(0.1, card.move_chance + field_chance)
        if random.uniform(0, 10) > chance:
            return 0.0
        return max(0.0, random.uniform(card.min_move, card.max_move + field_speed))

    @staticmethod
    async def _render(message: discord.Message, racers: list[_Racer],
                      round_no: int, field_chance: float, field_speed: float) -> None:
        embed = Embed(color=_RACE_COLOR)
        for racer in racers:
            filled = max(0, min(_TRACK_LENGTH, math.floor(racer.position)))
            track = f"{'▰' * filled}{racer.card.emoji}{'▱' * (_TRACK_LENGTH - filled)}🏁"
            embed.add_field(name=racer.name, value=track, inline=False)

        header = (f"🏁 Round {round_no}  ·  chance {field_chance:+g}  ·  "
                  f"speed {field_speed:+g}")
        await message.edit(content=header, embed=embed)

    async def _save_result(self, ctx: commands.Context, racers: list[_Racer], winner: _Racer) -> None:
        try:
            await self._stats.record_race([r.card.emoji for r in racers], winner.card.emoji)
        except Exception as e:
            Logger(__file__).message("Failed to record emoji race stats") \
                .context(ctx).exception(e).error()

    @commands.command(aliases=["racers", "racestats"])
    async def racerinfo(self, ctx: commands.Context):
        try:
            rows = {row["emoji"]: row for row in await self._stats.leaderboard()}
        except Exception as e:
            Logger(__file__).message("Failed to read emoji race stats") \
                .context(ctx).exception(e).error()
            await ctx.send("Racer stats are unavailable right now.")
            return

        embed = Embed(title="Emoji Racer Records", color=_RACE_COLOR)
        for card in EMOJI_RACERS:
            row = rows.get(card.emoji)
            wins = row["wins"] if row else 0
            races = row["total_races"] if row else 0
            win_rate = f"{round(wins / races * 100)}%" if races else "—"
            embed.add_field(
                name=card.emoji,
                value=f"Wins: {wins}\nLosses: {races - wins}\nWin rate: {win_rate}",
                inline=True,
            )
        await ctx.send(embed=embed)

    # --------------------------slots-----------------------------------------

    @commands.command()
    async def slots(self, ctx: commands.Context):
        grid = [[random.choice(_SLOT_EMOJIS) for _ in range(3)] for _ in range(3)]

        message = await ctx.send(embed=self._slot_embed(grid, revealed=1))
        for revealed in (2, 3):
            await asyncio.sleep(1)
            await message.edit(embed=self._slot_embed(grid, revealed=revealed))

        won = self._check_win(grid)
        await message.edit(content="🎉 Winner!" if won else "Try again.")

    @staticmethod
    def _check_win(grid: list[list[str]]) -> bool:
        lines = [
            *grid,
            *(list(col) for col in zip(*grid)),
            [grid[i][i] for i in range(3)],
            [grid[i][2 - i] for i in range(3)],
        ]
        return any(len(set(line)) == 1 for line in lines)

    @staticmethod
    def _slot_embed(grid: list[list[str]], revealed: int) -> Embed:
        hidden = "✴️"
        lines = []
        for r, row in enumerate(grid):
            left, right = ("▶️", "◀️") if r == 1 else ("⏹️", "⏹️")
            cells = "".join(cell if c < revealed else hidden for c, cell in enumerate(row))
            lines.append(f"{left}{cells}{right}")

        embed = Embed(title="SadDoug Slots", color=_SLOTS_COLOR)
        embed.add_field(name="​", value="\n".join(lines), inline=False)
        return embed


def setup(bot: DougBot):
    bot.add_cog(MinigameCommands(bot))