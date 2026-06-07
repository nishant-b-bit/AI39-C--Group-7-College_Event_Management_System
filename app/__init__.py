from flask import Flask, session
import config

def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    @app.context_processor
    def inject_notification_count():
        if "user_id" not in session:
            return {"unread_notifications": 0}
        from app.models.database import Database

        db = Database()
        result = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id=%s AND is_read=FALSE",
            (session["user_id"],),
        )
        db.close()
        return {"unread_notifications": result["cnt"] if result else 0}

    return app
