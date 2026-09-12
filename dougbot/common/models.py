from dougbot.common.database import Database


class Model:

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
        return db.execute(cls.ddl)

    @classmethod
    async def async_create(cls, db: Database) -> int:
        return await db.async_execute(cls.ddl)


_REGISTRY: list[type[Model]] = []


class EmojiRacerStats(Model):
    name = "minigame_emoji_racer_stats"
    ddl = f"""
        CREATE TABLE IF NOT EXISTS {name} (
            emoji       VARCHAR(64)  NOT NULL PRIMARY KEY,
            wins        INT UNSIGNED NOT NULL DEFAULT 0,
            total_races INT UNSIGNED NOT NULL DEFAULT 0
        )
    """


class BankAccounts(Model):
    name = "bank_accounts"
    ddl = f"""
        CREATE TABLE IF NOT EXISTS {name} (
            user_id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
            balance BIGINT UNSIGNED NOT NULL DEFAULT 0
        )
    """


def all_models() -> tuple[type[Model], ...]:
    return tuple(_REGISTRY)


def create_all(db: Database) -> None:
    for model in _REGISTRY:
        model.create(db)


async def async_create_all(db: Database) -> None:
    for model in _REGISTRY:
        await model.async_create(db)