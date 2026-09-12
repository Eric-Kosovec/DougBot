"""
MySQL database interface for DougBot.

Wraps a pooled SQLAlchemy engine (PyMySQL driver) behind a small set of
helpers. Connection details come from :func:`dougbot.config.get_configuration`,
which reads the ``DOUGBOT_DB_*`` environment variables in production and the
``[Database]`` section of ``dev_config.ini`` for local development.

Every helper takes a parameterised statement so callers never build SQL by
string concatenation, e.g.::

    from dougbot.common.database import get_database

    db = get_database()
    row = db.fetch_one(
        "SELECT balance FROM bank WHERE user_id = :user_id",
        {"user_id": ctx.author.id},
    )

The synchronous helpers block, so from a cog use the ``async_*`` variants,
which run the call in a worker thread and keep the event loop free.
"""

import asyncio
from contextlib import contextmanager
from typing import Any, Mapping, Optional, Sequence

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError

from dougbot import config
from dougbot.common.logger import Logger

Params = Optional[Mapping[str, Any]]

_DATABASE: Optional["Database"] = None


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""


class Database:
    """Thin wrapper around a pooled SQLAlchemy engine."""

    def __init__(self, engine: Engine):
        self._engine = engine

    @property
    def engine(self) -> Engine:
        return self._engine

    # -- reads ----------------------------------------------------------------

    def fetch_one(self, statement: str, params: Params = None) -> Optional[dict]:
        """Return the first row as a dict, or ``None`` if there are no rows."""
        with self._connect() as conn:
            row = conn.execute(text(statement), params or {}).mappings().first()
            return dict(row) if row is not None else None

    def fetch_all(self, statement: str, params: Params = None) -> list[dict]:
        """Return every row as a list of dicts."""
        with self._connect() as conn:
            rows = conn.execute(text(statement), params or {}).mappings().all()
            return [dict(row) for row in rows]

    def fetch_value(self, statement: str, params: Params = None) -> Any:
        """Return the first column of the first row (handy for COUNT/SUM/EXISTS)."""
        with self._connect() as conn:
            return conn.execute(text(statement), params or {}).scalar()

    # -- writes -------------------------------------------------------------- --

    def execute(self, statement: str, params: Params = None) -> int:
        """Run a write statement in its own transaction; return affected rows."""
        with self._begin() as conn:
            return conn.execute(text(statement), params or {}).rowcount

    def execute_many(self, statement: str, seq_of_params: Sequence[Mapping[str, Any]]) -> int:
        """Run one statement for each param mapping in a single transaction."""
        if not seq_of_params:
            return 0
        with self._begin() as conn:
            return conn.execute(text(statement), list(seq_of_params)).rowcount

    def insert(self, statement: str, params: Params = None) -> int:
        """Run an INSERT and return the generated AUTO_INCREMENT id."""
        with self._begin() as conn:
            return conn.execute(text(statement), params or {}).lastrowid

    @contextmanager
    def transaction(self):
        """Context manager yielding a connection with an open transaction.

        Commits on clean exit, rolls back on exception::

            with db.transaction() as conn:
                conn.execute(text("UPDATE bank SET balance = balance - :n WHERE user_id = :a"), ...)
                conn.execute(text("UPDATE bank SET balance = balance + :n WHERE user_id = :b"), ...)
        """
        with self._begin() as conn:
            yield conn

    # -- async wrappers -----------------------------------------------------------

    async def async_fetch_one(self, statement: str, params: Params = None) -> Optional[dict]:
        return await asyncio.to_thread(self.fetch_one, statement, params)

    async def async_fetch_all(self, statement: str, params: Params = None) -> list[dict]:
        return await asyncio.to_thread(self.fetch_all, statement, params)

    async def async_fetch_value(self, statement: str, params: Params = None) -> Any:
        return await asyncio.to_thread(self.fetch_value, statement, params)

    async def async_execute(self, statement: str, params: Params = None) -> int:
        return await asyncio.to_thread(self.execute, statement, params)

    async def async_execute_many(self, statement: str, seq_of_params: Sequence[Mapping[str, Any]]) -> int:
        return await asyncio.to_thread(self.execute_many, statement, seq_of_params)

    async def async_insert(self, statement: str, params: Params = None) -> int:
        return await asyncio.to_thread(self.insert, statement, params)

    # -- lifecycle ----------------------------------------------------------------

    def ping(self) -> bool:
        """Return ``True`` if a connection can be opened and queried."""
        try:
            with self._connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except DatabaseError:
            return False

    def dispose(self) -> None:
        """Close all pooled connections. Call on bot shutdown."""
        self._engine.dispose()

    # -- internals --------------------------------------------------------------

    @contextmanager
    def _connect(self):
        try:
            with self._engine.connect() as conn:
                yield conn
        except SQLAlchemyError as e:
            raise self._wrap(e)

    @contextmanager
    def _begin(self):
        try:
            with self._engine.begin() as conn:
                yield conn
        except SQLAlchemyError as e:
            raise self._wrap(e)

    @staticmethod
    def _wrap(exc: SQLAlchemyError) -> DatabaseError:
        Logger(__file__).message('Database operation failed').exception(exc).error()
        return DatabaseError(str(exc))


def _build_engine() -> Engine:
    configs = config.get_configuration()

    missing = [
        name for name in ('host', 'database', 'username', 'password')
        if not getattr(configs, name, None)
    ]
    if missing:
        raise DatabaseError(f"Database config incomplete, missing: {', '.join(missing)}")

    url = URL.create(
        drivername='mysql+pymysql',
        username=configs.username,
        password=configs.password,
        host=configs.host,
        port=configs.port,
        database=configs.database,
    )

    return create_engine(
        url,
        pool_size=configs.db_pool_size,
        max_overflow=configs.db_pool_size,
        pool_timeout=configs.db_connection_timeout,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_logging_name=configs.db_pool_name,
        connect_args={'connect_timeout': configs.db_connection_timeout},
        future=True,
    )


def get_database() -> Database:
    """Return the process-wide :class:`Database`, creating it on first use."""
    global _DATABASE
    if _DATABASE is None:
        _DATABASE = Database(_build_engine())
    return _DATABASE


def dispose_database() -> None:
    """Dispose of the process-wide database, if one was created."""
    global _DATABASE
    if _DATABASE is not None:
        _DATABASE.dispose()
        _DATABASE = None