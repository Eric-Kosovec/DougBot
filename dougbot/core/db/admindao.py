from dougbot.core.db.dougbotdb import DougBotDB


class AdminDAO:

    def __init__(self):
        db = DougBotDB()
        self.conn = db.get_connection()
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS admin (id text PRIMARY KEY, username text)")

    def get_admins(self):
        admins = []
        cur = self.conn.cursor()
        for admin_name in cur.execute("SELECT username FROM admin"):
            admins.append(admin_name)
        return admins

    def is_admin(self, admin_id):
        cur = self.conn.cursor()
        t = (str(admin_id), )
        cur.execute("SELECT * FROM admin WHERE id=?", t)
        found = cur.rowcount > 0
        return found

    def remove_admin(self, admin_id):
        cur = self.conn.cursor()
        t = (str(admin_id), )
        cur.execute("DELETE FROM admin WHERE id=?", t)
        self.conn.commit()

    def add_admin(self, admin_id, username):
        cur = self.conn.cursor()
        t = (str(admin_id), str(username))
        cur.execute("INSERT INTO admin VALUES (?, ?)", t)
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()
