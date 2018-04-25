import pdb
import os
import sqlite3


from utils.gen import print_exception
from utils.path import check_file_exists


class SqliteDatabase:
    def __init__(self, db_path, autocommit=False):
        self.db_path = os.path.expanduser(db_path)
        self.autocommit = autocommit
        self.conn = self.create_connection()

    def create_connection(self):
        """
            Create a database connection to a SQLite database

            :return: sqlite3.Connection object  or None
        """
        # Check if db file exists
        if not check_file_exists(self.db_path):
            print("Database filename '{}' doesn't exist".format(self.db_path))
            return None
        try:
            if self.autocommit:
                conn = sqlite3.connect(self.db_path, isolation_level=None)
            else:
                conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error:
            print_exception()
        return None

    def commit(self):
        """
        Wrapper to sqlite3.conn.commit()

        :return: None
        """
        if not self.autocommit:
            self.conn.commit()

    # TODO: add description; return number of items inserted
    def insert_many(self, tablename, values):
        sql = '''INSERT INTO %s VALUES (%s)''' % (tablename, ', '.join(map(str, ['?']*len(values[0]))))
        cur = self.conn.cursor()
        cur.executemany(sql, values)
        self.commit()
        return cur.rowcount


if __name__ == '__main__':
    pdb.set_trace()
