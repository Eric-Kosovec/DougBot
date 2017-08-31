from db.dougbotdb import DougBotDB


class AdminDAO:

    def __init__(self):
        db = DougBotDB()
        self.conn = db.get_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin'")
        #if cur.rowcount <= 0:
            #cur.execute("CREATE TABLE admin (id text)")
            #self.conn.commit()
        return

    def get_admins(self):
        admins = []
        cur = self.conn.cursor()
        for admin_id in cur.execute("SELECT id FROM admin"):
            admins.append(admin_id)
        return admins

    def is_admin(self, admin_id):
        cur = self.conn.cursor()
        t = (str(admin_id), )
        cur.execute("SELECT * FROM admin WHERE id=?", t)
        found = cur.rowcount > 0
        self.conn.commit()
        return found

    def remove_admin(self, admin_id):
        cur = self.conn.cursor()
        t = (str(admin_id), )
        cur.execute("DELETE FROM admin WHERE id=?", t)
        self.conn.commit()

    def add_admin(self, admin_id):
        cur = self.conn.cursor()
        t = (str(admin_id), )
        cur.execute("INSERT INTO admin VALUES (?)", t)
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()
