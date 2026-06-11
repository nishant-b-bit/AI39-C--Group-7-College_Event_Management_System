from functools import wraps
import hashlib

from flask import flash, redirect, session, url_for

from app.models.database import Database


def hash_password(password):
    """Hash a password with SHA-256 to match the existing users table."""
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    """Redirect to login if the user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Allow only users with one of the given roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                flash("You do not have permission to access that page.", "danger")
                return redirect(url_for("auth.home"))
            return f(*args, **kwargs)
        return decorated
    return decorator


def notify_user(user_id, message):
    db = Database()
    db.execute(
        "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
        (user_id, message),
    )
    db.close()


def notify_students(message):
    db = Database()
    db.execute(
        """
        INSERT INTO notifications (user_id, message)
        SELECT id, %s
        FROM users
        WHERE role='student'
        """,
        (message,),
    )
    db.close()


def promote_waitlisted_student(event_id, event_title):
    db = Database()
    moved = db.fetch_one("""
        SELECT id, student_id
        FROM registrations
        WHERE event_id=%s AND status='waitlisted'
        ORDER BY registered_at ASC
        LIMIT 1
    """, (event_id,))
    if moved:
        db.execute("UPDATE registrations SET status='selected' WHERE id=%s", (moved["id"],))
        db.close()
        notify_user(moved["student_id"], f"You were moved from waitlist to selected for {event_title}.")
        return True
    db.close()
    return False
