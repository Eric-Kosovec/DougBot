from dougbot.core.db.dougbotdb import DougBotDB


class AdminDAO:

    def __init__(self):
        self._db = DougBotDB()
        self._conn = self._open()
        cur = self._conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS admin (id text PRIMARY KEY, username text)")

    def get_admins(self):
        admins = []
        cur = self._conn.cursor()
        for admin_name in cur.execute("SELECT username FROM admin"):
            admins.append(admin_name)
        return admins

    def is_admin(self, admin_id):
        cur = self._conn.cursor()
        t = (str(admin_id), )
        cur.execute("SELECT * FROM admin WHERE id=?", t)
        found = cur.rowcount > 0
        return found

    def remove_admin(self, admin_id):
        cur = self._conn.cursor()
        t = (str(admin_id), )
        cur.execute("DELETE FROM admin WHERE id=?", t)
        self._conn.commit()

    def add_admin(self, admin_id, username):
        cur = self._conn.cursor()
        t = (str(admin_id), str(username))
        cur.execute("INSERT INTO admin VALUES (?, ?)", t)
        self._conn.commit()

    def _open(self):
        if self._conn is not None:
            return self._conn
        return self._db.get_connection()

    def close(self):
        if self._conn is not None:
            self._conn.commit()
            self._conn.close()
            self._conn = None
