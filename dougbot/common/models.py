"""Database schema definitions for DougBot.

The project talks to MySQL through the thin raw-SQL helper in
:mod:`dougbot.common.database` rather than an ORM, so a "model" here is just a
table name plus the ``CREATE TABLE IF NOT EXISTS`` statement that brings it
into existence. Feature code imports the model it needs and calls
``await Model.create(db)`` (or :func:`create_all`) during start-up.
"""

from dougbot.common.database import Database


class Model:
    """Base class for a single table's schema."""

    #: Table name as it appears in SQL.
    name: str = ""
    #: ``CREATE TABLE IF NOT EXISTS`` statement for the table.
    ddl: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.name or not cls.ddl:
            raise ValueError(f"{cls.__name__} must define both 'name' and 'ddl'")
        _REGISTRY.append(cls)

    @classmethod
    def create(cls, db: Database) -> int:
        """Create the table if it does not already exist."""
        return db.execute(cls.ddl)

    @classmethod
    async def async_create(cls, db: Database) -> int:
        return await db.async_execute(cls.ddl)


_REGISTRY: list[type[Model]] = []


class EmojiRacerStats(Model):
    """Win/loss tally for the emoji drag race minigame.

    One row per racer emoji; rows are upserted as races complete.
    """

    name = "minigame_emoji_racer_stats"
    ddl = f"""
        CREATE TABLE IF NOT EXISTS {name} (
            emoji       VARCHAR(64)  NOT NULL PRIMARY KEY,
            wins        INT UNSIGNED NOT NULL DEFAULT 0,
            total_races INT UNSIGNED NOT NULL DEFAULT 0
        )
    """


def all_models() -> tuple[type[Model], ...]:
    """Every registered model, in definition order."""
    return tuple(_REGISTRY)


def create_all(db: Database) -> None:
    """Create every registered table that does not yet exist.

    Called once from :meth:`dougbot.core.bot.DougBot.run` during start-up,
    before the gateway connection is opened.
    """
    for model in _REGISTRY:
        model.create(db)


async def async_create_all(db: Database) -> None:
    """Async variant of :func:`create_all`."""
    for model in _REGISTRY:
        await model.async_create(db)