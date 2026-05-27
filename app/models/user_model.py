from app.models.database import Database

class User:

    @staticmethod
    def create_user(name, email, password, role):
        db = Database()
        cursor = db._Database__connection.cursor()

        query = """
        INSERT INTO users(name, email, password, role)
        VALUES(%s, %s, %s, %s)
        """

        cursor.execute(query, (name, email, password, role))

        db._Database__connection.commit()
        cursor.close()
        db.close()

    @staticmethod
    def login_user(email, password):
        db = Database()
        cursor = db._Database__connection.cursor(pymysql.cursors.DictCursor)

        query = """
        SELECT * FROM users WHERE email=%s AND password=%s
        """

        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        return user