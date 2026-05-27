import pymysql
import config

class Database:
    def __init__(self):
        """ open a database connection when object is created."""
        try:
            self.__connection=pymysql.connect(
                host=config.mysql_host,
                user=config.mysql_user,
                password=config.mysql_password,
                database=config.mysql_database,
                cursorclass=pymysql.cursors.DictCursor,
            )
            print("Database connected Sucessfully!")
        except pymysql.MySQLError as e:
            print('Database connection failed!')
            print("error:",e)
    
    def fetch_one(self, query, params=None):
        """Run a query and return ONE result (or None)."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        """Run a query and return ALL results as a list."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results

    def execute(self, query, params=None):
        """Run a query that changes data (INSERT, UPDATE, DELETE)."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        self.__connection.commit()
        cursor.close()

    def close(self):
        """Close the database connection."""
        self.__connection.close()
                        
    # ── Static Method: Create tables on app startup ─────────

    @staticmethod
    def create_tables():
        """
        Create database tables if they don't exist.

        @staticmethod: belongs to the class but doesn't need
        'self' — it doesn't use any instance data.
        You call it as: Database.create_tables()
        """
        db = Database()
        db.execute("""
           CREATE TABLE users (
               id INT AUTO_INCREMENT PRIMARY KEY,
               name VARCHAR(100),
               email VARCHAR(100) UNIQUE,
               password VARCHAR(255),
               role VARCHAR(20)
            )
        """)
        

        db.close()