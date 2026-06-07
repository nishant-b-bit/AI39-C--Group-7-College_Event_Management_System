from flask import flash, redirect, render_template, request, session, url_for

from app.controllers.helpers import hash_password, login_required
from app.models.database import Database


class AuthController:
    def home(self):
        return render_template("home.html")

    def about(self):
        return render_template("about.html")

    def contact(self):
        return render_template("contact.html")

    def base(self):
        return render_template("common/base.html")

    def login(self):
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            if not email or not password:
                flash("Email and password are required.", "danger")
                return render_template("login.html")

            db = Database()
            hashed_password = hash_password(password)
            user = db.fetch_one(
                "SELECT * FROM users WHERE email=%s AND password=%s",
                (email, hashed_password)
            )
            if not user:
                user = db.fetch_one(
                    "SELECT * FROM users WHERE email=%s AND password=%s",
                    (email, password),
                )
                if user:
                    db.execute(
                        "UPDATE users SET password=%s WHERE id=%s",
                        (hashed_password, user["id"]),
                    )
            db.close()

            if user:
                session["user_id"] = user["id"]
                session["role"] = user["role"]
                session["name"] = user["name"]

                if user["role"] == "student":
                    return redirect(url_for("auth.student_dashboard"))
                if user["role"] == "organizer":
                    return redirect(url_for("auth.organizer_dashboard"))
                if user["role"] == "admin":
                    return redirect(url_for("auth.admin_dashboard"))

            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        return render_template("login.html")

    def register(self):
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            requested_role = request.form.get("role", "student")
            if requested_role not in ("student", "organizer"):
                requested_role = "student"

            if not name or not email or not password:
                flash("All fields are required.", "danger")
                return render_template("signup.html")

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("signup.html")

            db = Database()
            existing = db.fetch_one("SELECT id FROM users WHERE email=%s", (email,))
            if existing:
                db.close()
                flash("An account with that email already exists.", "danger")
                return render_template("signup.html")

            db.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hash_password(password), requested_role)
            )
            db.close()

            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))

        return render_template("signup.html")

    def logout(self):
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("auth.login"))

    @login_required
    def edit_profile(self):
        db = Database()
        user = db.fetch_one(
            "SELECT id, name, email, phone, college, role FROM users WHERE id=%s",
            (session["user_id"],),
        )
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            college = request.form.get("college", "").strip()
            if not name:
                flash("Name is required.", "danger")
                db.close()
                return render_template("edit_profile.html", user=user)

            db.execute(
                "UPDATE users SET name=%s, phone=%s, college=%s WHERE id=%s",
                (name, phone, college, session["user_id"]),
            )
            db.close()
            session["name"] = name
            flash("Profile updated.", "success")
            return redirect(url_for("auth.edit_profile"))

        db.close()
        return render_template("edit_profile.html", user=user)

    @login_required
    def change_password(self):
        if request.method == "POST":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return render_template("change_password.html")
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("change_password.html")

            db = Database()
            user = db.fetch_one(
                "SELECT id FROM users WHERE id=%s AND password=%s",
                (session["user_id"], hash_password(current_password)),
            )
            if not user:
                db.close()
                flash("Current password is incorrect.", "danger")
                return render_template("change_password.html")

            db.execute(
                "UPDATE users SET password=%s WHERE id=%s",
                (hash_password(new_password), session["user_id"]),
            )
            db.close()
            flash("Password changed.", "success")
            return redirect(url_for("auth.edit_profile"))

        return render_template("change_password.html")

    def reset_password(self):
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if len(new_password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("reset_password.html")
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("reset_password.html")

            db = Database()
            user = db.fetch_one("SELECT id FROM users WHERE email=%s", (email,))
            if not user:
                db.close()
                flash("No account found with that email.", "danger")
                return render_template("reset_password.html")

            db.execute(
                "UPDATE users SET password=%s WHERE email=%s",
                (hash_password(new_password), email),
            )
            db.close()
            flash("Password reset. Please log in.", "success")
            return redirect(url_for("auth.login"))

        return render_template("reset_password.html")

    @login_required
    def notifications(self):
        db = Database()
        notifications = db.fetch_all(
            "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC",
            (session["user_id"],),
        )
        db.execute("UPDATE notifications SET is_read=TRUE WHERE user_id=%s", (session["user_id"],))
        db.close()
        return render_template("notifications.html", notifications=notifications)

    @login_required
    def view_events(self):
        search = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()
        event_date = request.args.get("date", "").strip()
        db = Database()
        filters = ["e.status = 'approved'", "e.event_status != 'cancelled'"]
        params = []
        if search:
            filters.append("(e.title LIKE %s OR e.description LIKE %s OR e.location LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if category:
            filters.append("COALESCE(c.name, e.genre) = %s")
            params.append(category)
        if event_date:
            filters.append("e.date = %s")
            params.append(event_date)

        events = db.fetch_all(f"""
            SELECT e.*, u.name AS organizer_name,
                   COALESCE(c.name, e.genre) AS category_name,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.id AND status='selected') AS registered
            FROM events e
            JOIN users u ON e.organizer_id = u.id
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE {' AND '.join(filters)}
            ORDER BY e.date ASC
        """, tuple(params))
        categories = db.fetch_all("SELECT name FROM categories ORDER BY name")
        db.close()
        return render_template(
            "view_events.html",
            events=events,
            categories=categories,
            filters={"search": search, "category": category, "date": event_date},
        )

    @login_required
    def eventdetails(self):
        event_id = request.args.get("id")
        db = Database()
        event = db.fetch_one("""
            SELECT e.*, u.name AS organizer_name,
                   COALESCE(c.name, e.genre) AS category_name,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.id AND status='selected') AS registered
            FROM events e
            JOIN users u ON e.organizer_id = u.id
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.id = %s AND e.status = 'approved'
        """, (event_id,))
        announcements = db.fetch_all(
            "SELECT * FROM announcements WHERE event_id=%s ORDER BY created_at DESC",
            (event_id,),
        )
        db.close()
        if not event:
            flash("Event not found.", "danger")
            return redirect(url_for("auth.view_events"))
        return render_template("event_details.html", event=event, announcements=announcements)
