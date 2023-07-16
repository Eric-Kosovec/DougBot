from dougbot.common import database

class BankLib:

    def get_user_amount(self, discord_user_id: str) -> int:
        conn = database.connect()
        result = database.mysql_select(conn,'SELECT * FROM dougbot.bank WHERE user_id = ' + discord_user_id)
        return result[0]

    def modify_amount(self, amount: int, discord_user_id: str):
        conn = database.connect()
        amount =
        rows = database.mysql_update(conn, 'UPDATE dougbot.bank set ')