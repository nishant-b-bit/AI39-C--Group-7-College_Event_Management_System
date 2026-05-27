import mysql.connector

class Database:
    @staticmethod
    def connect():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="21Apr2124",
            database="event_management"
        )