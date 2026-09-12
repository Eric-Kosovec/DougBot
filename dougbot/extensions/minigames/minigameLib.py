from typing import Optional

from dougbot.common.database import Database, get_database
from dougbot.common.models import EmojiRacerStats as EmojiRacerStatsModel

_TABLE = EmojiRacerStatsModel.name

_RECORD = f"""
    INSERT INTO {_TABLE} (emoji, wins, total_races)
    VALUES (:emoji, :won, 1)
    ON DUPLICATE KEY UPDATE
        wins = wins + :won,
        total_races = total_races + 1
"""

_LEADERBOARD = f"""
    SELECT emoji, wins, total_races
    FROM {_TABLE}
    ORDER BY wins DESC, total_races ASC
"""


class EmojiRacerStore:
    """MySQL-backed win/loss tally for the emoji racers."""

    def __init__(self, database: Optional[Database] = None):
        self._db = database

    @property
    def _database(self) -> Database:
        if self._db is None:
            self._db = get_database()
        return self._db

    async def record_race(self, participants: list[str], winner: str) -> None:
        """Add one race: every participant gets +1 race, the winner also +1 win."""
        rows = [
            {"emoji": emoji, "won": 1 if emoji == winner else 0}
            for emoji in dict.fromkeys(participants)  # de-dupe, keep order
        ]
        if rows:
            await self._database.async_execute_many(_RECORD, rows)

    async def leaderboard(self) -> list[dict]:
        """Return every stored row, best record first."""
        return await self._database.async_fetch_all(_LEADERBOARD)