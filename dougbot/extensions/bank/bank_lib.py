from typing import Optional

from dougbot.common.database import Database, get_database
from dougbot.common.models import BankAccounts as BankAccountsModel

_TABLE = BankAccountsModel.name

_IS_ENROLLED = f"SELECT 1 FROM {_TABLE} WHERE user_id = :user_id"
_GET_BALANCE = f"SELECT balance FROM {_TABLE} WHERE user_id = :user_id"
_ENROLL = f"INSERT IGNORE INTO {_TABLE} (user_id, balance) VALUES (:user_id, 0)"
_DEPOSIT = f"""
    UPDATE {_TABLE} SET balance = balance + :amount WHERE user_id = :user_id
"""
_WITHDRAW = f"""
    UPDATE {_TABLE} SET balance = balance - :amount
    WHERE user_id = :user_id AND balance >= :amount
"""
_PAY_ALL = f"UPDATE {_TABLE} SET balance = balance + :amount"


class BankError(RuntimeError):

class NotEnrolledError(BankError):

    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} is not enrolled in the bank")
        self.user_id = user_id


class InsufficientFundsError(BankError):

    def __init__(self, user_id: int, balance: int, amount: int):
        super().__init__(f"User {user_id} has {balance}, cannot withdraw {amount}")
        self.user_id = user_id
        self.balance = balance
        self.amount = amount


class BankStore:

    def __init__(self, database: Optional[Database] = None):
        self._db = database

    @property
    def _database(self) -> Database:
        if self._db is None:
            self._db = get_database()
        return self._db

    async def is_enrolled(self, user_id: int) -> bool:
        row = await self._database.async_fetch_one(_IS_ENROLLED, {"user_id": user_id})
        return row is not None

    async def enroll(self, user_id: int) -> bool:
        affected = await self._database.async_execute(_ENROLL, {"user_id": user_id})
        return affected > 0

    async def get_balance(self, user_id: int) -> Optional[int]:
        row = await self._database.async_fetch_one(_GET_BALANCE, {"user_id": user_id})
        return row["balance"] if row is not None else None

    async def deposit(self, user_id: int, amount: int) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")

        affected = await self._database.async_execute(_DEPOSIT, {"user_id": user_id, "amount": amount})
        if affected == 0:
            raise NotEnrolledError(user_id)
        return await self.get_balance(user_id)

    async def withdraw(self, user_id: int, amount: int) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")

        affected = await self._database.async_execute(_WITHDRAW, {"user_id": user_id, "amount": amount})
        if affected == 0:
            balance = await self.get_balance(user_id)
            if balance is None:
                raise NotEnrolledError(user_id)
            raise InsufficientFundsError(user_id, balance, amount)
        return await self.get_balance(user_id)

    async def pay_all(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return await self._database.async_execute(_PAY_ALL, {"amount": amount})