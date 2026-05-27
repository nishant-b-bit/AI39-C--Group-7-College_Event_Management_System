from app.models.database import Database

class User:

    @staticmethod
    def create_user(name, email, password, role):
        conn = Database.connect()
        cursor = conn.cursor()

        query = """
        INSERT INTO users(name, email, password, role)
        VALUES(%s, %s, %s, %s)
        """

        cursor.execute(query, (name, email, password, role))

        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def login_user(email, password):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM users WHERE email=%s AND password=%s
        """

        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return user