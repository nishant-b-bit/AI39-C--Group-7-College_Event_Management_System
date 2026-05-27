import mysql.connector

class Database:
    @staticmethod
    def connect():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="yourpassword",
            database="event_management"
        )