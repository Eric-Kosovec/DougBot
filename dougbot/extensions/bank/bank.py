from datetime import datetime, time

from dateutil.tz import tz
from discord.ext import commands, tasks

from dougbot.common.logger import Logger
from dougbot.core.bot import DougBot
from dougbot.extensions.bank.bank_lib import BankStore

_TIMEZONE = tz.gettz('America/Chicago')
_PAYCHECK_TIME = time(hour=9, tzinfo=_TIMEZONE)
_PAYCHECK_WEEKDAY = 4  # Friday
_BASE_PAY = 25


class Bank(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        self._store = BankStore()
        self._paycheck.start()

    def cog_unload(self):
        self._paycheck.cancel()

    # --------------------------commands---------------------------------------

    @commands.command(name="bankenroll")
    async def bank_enroll(self, ctx: commands.Context):
        if await self._store.enroll(ctx.author.id):
            await ctx.send(f"{ctx.author.mention} You've opened a bank account. Balance: 0")
        else:
            await ctx.send(f"{ctx.author.mention} You already have a bank account.")

    @commands.command(name="balance", aliases=["bankbalance"])
    async def bank_balance(self, ctx: commands.Context):
        balance = await self.get_balance(ctx.author.id)
        if balance is None:
            await ctx.send(f"{ctx.author.mention} You don't have a bank account. Run `bankEnroll` first.")
        else:
            await ctx.send(f"{ctx.author.mention} Balance: {balance}")

    # --------------------------interface for other extensions-----------------

    async def is_enrolled(self, user_id: int) -> bool:
        return await self._store.is_enrolled(user_id)

    async def get_balance(self, user_id: int) -> int | None:
        return await self._store.get_balance(user_id)

    async def deposit(self, user_id: int, amount: int) -> int:
        return await self._store.deposit(user_id, amount)

    async def withdraw(self, user_id: int, amount: int) -> int:
        return await self._store.withdraw(user_id, amount)

    # --------------------------paycheck----------------------------------------

    @tasks.loop(time=_PAYCHECK_TIME)
    async def _paycheck(self):
        if datetime.now(_TIMEZONE).weekday() != _PAYCHECK_WEEKDAY:
            return

        try:
            paid = await self._store.pay_all(_BASE_PAY)
            Logger(__file__).message(f"Paid {paid} users a {_BASE_PAY} paycheck").info()
        except Exception as e:
            Logger(__file__).message("Failed to run bank paycheck").exception(e).error()


def setup(bot: DougBot):
    bot.add_cog(Bank(bot))