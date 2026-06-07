import pymysql
import config

class Database:
    def __init__(self):
        """Open a database connection when object is created."""
        try:
            self.__connection = pymysql.connect(
                host=config.mysql_host,
                user=config.mysql_user,
                password=config.mysql_password,
                database=config.mysql_database,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        except pymysql.MySQLError as e:
            print('Database connection failed!')
            print("error:", e)
            self.__connection = None

    def fetch_one(self, query, params=None):
        """Run a query and return ONE result (or None)."""
        if not self.__connection:
            return None
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        """Run a query and return ALL results as a list."""
        if not self.__connection:
            return []
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results

    def execute(self, query, params=None):
        """Run a query that changes data (INSERT, UPDATE, DELETE).
        Returns lastrowid for INSERT statements."""
        if not self.__connection:
            return None
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        lastrowid = cursor.lastrowid
        cursor.close()
        return lastrowid

    def close(self):
        """Close the database connection."""
        if self.__connection:
            self.__connection.close()

    @property
    def is_connected(self):
        return self.__connection is not None

    @staticmethod
    def create_tables():
        from app.models.schema import create_tables

        create_tables()
