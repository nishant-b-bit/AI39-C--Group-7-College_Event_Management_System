from flask import flash, redirect, render_template, request, session, url_for

from app.controllers.helpers import login_required, notify_user, role_required
from app.models.database import Database


class AdminController:
    @login_required
    @role_required("admin")
    def admin_dashboard(self):
        db = Database()
        total_users = db.fetch_one("SELECT COUNT(*) AS cnt FROM users")["cnt"]
        total_events = db.fetch_one("SELECT COUNT(*) AS cnt FROM events")["cnt"]
        pending_approvals = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM events WHERE status='pending'")["cnt"]
        total_organizers = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM users WHERE role='organizer'")["cnt"]
        total_registrations = db.fetch_one("SELECT COUNT(*) AS cnt FROM registrations")["cnt"]
        total_categories = db.fetch_one("SELECT COUNT(*) AS cnt FROM categories")["cnt"]
        events_by_status = db.fetch_all("""
            SELECT event_status, COUNT(*) AS cnt
            FROM events
            GROUP BY event_status
        """)

        pending_events = db.fetch_all("""
            SELECT e.*, u.name AS organizer_name
            FROM events e JOIN users u ON e.organizer_id = u.id
            WHERE e.status = 'pending'
            ORDER BY e.created_at DESC
            LIMIT 5
        """)
        db.close()

        stats = {
            "total_users": total_users,
            "total_events": total_events,
            "pending_approvals": pending_approvals,
            "total_organizers": total_organizers,
            "total_registrations": total_registrations,
            "total_categories": total_categories,
        }
        return render_template("admin_dashboard.html", stats=stats,
                               pending_events=pending_events,
                               events_by_status=events_by_status)

    @login_required
    @role_required("admin")
    def approve_events(self):
        db = Database()
        events = db.fetch_all("""
            SELECT e.*, u.name AS organizer_name, COALESCE(c.name, e.genre) AS category_name
            FROM events e JOIN users u ON e.organizer_id = u.id
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.status = 'pending'
            ORDER BY e.created_at DESC
        """)
        db.close()
        return render_template("approve_events.html", events=events)

    @login_required
    @role_required("admin")
    def approve_event_action(self, event_id):
        action = request.form.get("action")
        if action not in ("approved", "rejected"):
            flash("Invalid action.", "danger")
            return redirect(url_for("auth.approve_events"))

        db = Database()
        event = db.fetch_one("SELECT title, organizer_id FROM events WHERE id=%s", (event_id,))
        if not event:
            db.close()
            flash("Event not found.", "danger")
            return redirect(url_for("auth.approve_events"))
        db.execute("UPDATE events SET status=%s WHERE id=%s", (action, event_id))
        db.close()
        notify_user(event["organizer_id"], f"Event {action}: {event['title']}.")
        flash(f"Event {action}.", "success")
        return redirect(url_for("auth.approve_events"))

    @login_required
    @role_required("admin")
    def manage_users(self):
        db = Database()
        users = db.fetch_all(
            "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")
        db.close()
        return render_template("manage_users.html", users=users)

    @login_required
    @role_required("admin")
    def delete_user(self, user_id):
        if int(user_id) == session["user_id"]:
            flash("You cannot delete your own account.", "danger")
            return redirect(url_for("auth.manage_users"))
        db = Database()
        db.execute("DELETE FROM users WHERE id=%s", (user_id,))
        db.close()
        flash("User deleted.", "success")
        return redirect(url_for("auth.manage_users"))

    @login_required
    @role_required("admin")
    def change_user_role(self, user_id):
        new_role = request.form.get("role")
        if new_role not in ("student", "organizer", "admin"):
            flash("Invalid role.", "danger")
            return redirect(url_for("auth.manage_users"))
        db = Database()
        db.execute("UPDATE users SET role=%s WHERE id=%s", (new_role, user_id))
        db.close()
        flash("User role updated.", "success")
        return redirect(url_for("auth.manage_users"))

    @login_required
    @role_required("admin")
    def manage_categories(self):
        db = Database()
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            if not name:
                flash("Category name is required.", "danger")
            else:
                existing = db.fetch_one("SELECT id FROM categories WHERE name=%s", (name,))
                if existing:
                    flash("That category already exists.", "warning")
                else:
                    db.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
                    flash("Category added.", "success")
            db.close()
            return redirect(url_for("auth.manage_categories"))

        categories = db.fetch_all("""
            SELECT c.*, COUNT(e.id) AS event_count
            FROM categories c
            LEFT JOIN events e ON e.category_id = c.id
            GROUP BY c.id
            ORDER BY c.name
        """)
        db.close()
        return render_template("manage_categories.html", categories=categories)

    @login_required
    @role_required("admin")
    def delete_category(self, category_id):
        db = Database()
        db.execute("UPDATE events SET category_id=NULL WHERE category_id=%s", (category_id,))
        db.execute("DELETE FROM categories WHERE id=%s", (category_id,))
        db.close()
        flash("Category deleted. Existing events were moved to their typed category text.", "success")
        return redirect(url_for("auth.manage_categories"))
