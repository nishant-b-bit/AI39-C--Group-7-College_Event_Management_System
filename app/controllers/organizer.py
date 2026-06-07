import csv
from io import StringIO

from flask import Response, flash, redirect, render_template, request, session, url_for

from app.controllers.helpers import login_required, notify_user, promote_waitlisted_student, role_required
from app.models.database import Database


class OrganizerController:
    @login_required
    @role_required("organizer")
    def organizer_dashboard(self):
        db = Database()
        events = db.fetch_all("""
            SELECT e.*,
                   COALESCE(c.name, e.genre) AS category_name,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.id AND status='selected') AS registrations,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.id AND status='waitlisted') AS waitlisted
            FROM events e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.organizer_id = %s
            ORDER BY e.created_at DESC
        """, (session["user_id"],))

        stats = {
            "total_events": len(events),
            "active_events": sum(1 for e in events if e["status"] == "approved"),
            "total_registrations": sum(e["registrations"] for e in events),
            "pending_approval": sum(1 for e in events if e["status"] == "pending"),
        }
        db.close()
        return render_template("organizer_dashboard.html", events=events, stats=stats)

    @login_required
    @role_required("organizer")
    def create_events(self):
        db = Database()
        categories = db.fetch_all("SELECT id, name FROM categories ORDER BY name")
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            genre = request.form.get("genre", "").strip()
            category_id = request.form.get("category_id") or None
            event_date = request.form.get("date", "")
            time = request.form.get("time", "")
            location = request.form.get("location", "").strip()
            capacity = request.form.get("capacity", 100)
            event_status = request.form.get("event_status", "upcoming")
            description = request.form.get("description", "").strip()
            if event_status not in ("upcoming", "ongoing", "completed", "cancelled"):
                event_status = "upcoming"

            if not title or not event_date or not location:
                flash("Title, date and location are required.", "danger")
                db.close()
                return render_template("create_events.html", categories=categories)

            db.execute("""
                INSERT INTO events
                    (title, genre, category_id, date, time, location, capacity,
                     description, organizer_id, status, event_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s)
            """, (
                title, genre, category_id, event_date, time, location, capacity,
                description, session["user_id"], event_status,
            ))
            db.close()

            flash("Event submitted for approval!", "success")
            return redirect(url_for("auth.organizer_dashboard"))

        db.close()
        return render_template("create_events.html", categories=categories)

    @login_required
    @role_required("organizer")
    def edit_event(self, event_id):
        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        categories = db.fetch_all("SELECT id, name FROM categories ORDER BY name")

        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            genre = request.form.get("genre", "").strip()
            category_id = request.form.get("category_id") or None
            event_date = request.form.get("date", "")
            time = request.form.get("time", "")
            location = request.form.get("location", "").strip()
            capacity = request.form.get("capacity", 100)
            event_status = request.form.get("event_status", "upcoming")
            description = request.form.get("description", "").strip()
            if event_status not in ("upcoming", "ongoing", "completed", "cancelled"):
                event_status = "upcoming"

            db.execute("""
                UPDATE events SET title=%s, genre=%s, category_id=%s, date=%s, time=%s, location=%s,
                capacity=%s, description=%s, event_status=%s, status='pending'
                WHERE id=%s AND organizer_id=%s
            """, (title, genre, category_id, event_date, time, location, capacity, description, event_status,
                  event_id, session["user_id"]))
            db.close()
            flash("Event updated. It will need re-approval.", "success")
            return redirect(url_for("auth.organizer_dashboard"))

        db.close()
        return render_template("edit_event.html", event=event, categories=categories)

    @login_required
    @role_required("organizer")
    def delete_event(self, event_id):
        db = Database()
        db.execute(
            "DELETE FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        db.close()
        flash("Event deleted.", "success")
        return redirect(url_for("auth.organizer_dashboard"))

    @login_required
    @role_required("organizer")
    def participants(self, event_id):
        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))

        participants = db.fetch_all("""
            SELECT r.id AS registration_id, u.name, u.email, u.phone, u.college,
                   r.registered_at, r.attended, r.status, r.certificate_available
            FROM registrations r
            JOIN users u ON r.student_id = u.id
            WHERE r.event_id = %s
            ORDER BY r.registered_at ASC
        """, (event_id,))
        db.close()
        return render_template("participants.html", participants=participants, event=event)

    @login_required
    @role_required("organizer")
    def download_participants_csv(self, event_id):
        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))

        participants = db.fetch_all("""
            SELECT u.name, u.email, u.phone, u.college, r.status, r.attended, r.registered_at
            FROM registrations r
            JOIN users u ON r.student_id = u.id
            WHERE r.event_id=%s
            ORDER BY r.registered_at ASC
        """, (event_id,))
        db.close()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Email", "Phone", "College", "Registration Status", "Attended", "Registered At"])
        for p in participants:
            writer.writerow([
                p["name"], p["email"], p.get("phone") or "", p.get("college") or "",
                p["status"], "Yes" if p["attended"] else "No", p["registered_at"],
            ])
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=participants-{event_id}.csv"},
        )

    @login_required
    @role_required("organizer")
    def attendance(self, event_id):
        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))

        if request.method == "POST":
            attended_ids = request.form.getlist("attended")
            db.execute("UPDATE registrations SET attended=FALSE WHERE event_id=%s", (event_id,))
            for student_id in attended_ids:
                db.execute(
                    """UPDATE registrations
                       SET attended=TRUE, certificate_available=TRUE
                       WHERE event_id=%s AND student_id=%s AND status='selected'""",
                    (event_id, student_id))
                notify_user(student_id, f"Certificate available for {event['title']}.")
            db.close()
            flash("Attendance saved.", "success")
            return redirect(url_for("auth.attendance", event_id=event_id))

        participants = db.fetch_all("""
            SELECT u.id AS student_id, u.name, u.email, r.attended, r.status
            FROM registrations r
            JOIN users u ON r.student_id = u.id
            WHERE r.event_id = %s AND r.status='selected'
        """, (event_id,))
        db.close()
        return render_template("attendance.html", participants=participants, event=event)

    @login_required
    @role_required("organizer")
    def event_capacity(self, event_id):
        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))

        registered = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM registrations WHERE event_id=%s AND status='selected'",
            (event_id,))["cnt"]
        attended = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM registrations WHERE event_id=%s AND attended=TRUE",
            (event_id,))["cnt"]
        db.close()

        capacity_data = {
            "title": event["title"],
            "capacity": event["capacity"],
            "registered": registered,
            "remaining": event["capacity"] - registered,
            "attendance": attended,
        }
        return render_template("event_capacity.html", event=capacity_data)

    @login_required
    @role_required("organizer")
    def update_event_capacity(self, event_id):
        capacity = request.form.get("capacity", type=int)
        if not capacity or capacity < 1:
            flash("Capacity must be at least 1.", "danger")
            return redirect(url_for("auth.event_capacity", event_id=event_id))

        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))
        db.execute("UPDATE events SET capacity=%s WHERE id=%s", (capacity, event_id))
        selected = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM registrations WHERE event_id=%s AND status='selected'",
            (event_id,),
        )["cnt"]
        db.close()
        while selected < capacity and promote_waitlisted_student(event_id, event["title"]):
            selected += 1
        flash("Capacity updated.", "success")
        return redirect(url_for("auth.event_capacity", event_id=event_id))

    @login_required
    @role_required("organizer")
    def announcements(self, event_id):
        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))

        if request.method == "POST":
            message = request.form.get("message", "").strip()
            if not message:
                flash("Announcement message is required.", "danger")
            else:
                db.execute(
                    "INSERT INTO announcements (event_id, message) VALUES (%s, %s)",
                    (event_id, message),
                )
                students = db.fetch_all(
                    "SELECT student_id FROM registrations WHERE event_id=%s AND status IN ('selected', 'waitlisted')",
                    (event_id,),
                )
                db.close()
                for student in students:
                    notify_user(student["student_id"], f"Announcement for {event['title']}: {message[:180]}")
                flash("Announcement posted.", "success")
                return redirect(url_for("auth.announcements", event_id=event_id))

        announcements = db.fetch_all(
            "SELECT * FROM announcements WHERE event_id=%s ORDER BY created_at DESC",
            (event_id,),
        )
        db.close()
        return render_template("announcements.html", event=event, announcements=announcements)

    @login_required
    @role_required("organizer")
    def manage_registration_status(self, event_id):
        registration_id = request.form.get("registration_id")
        new_status = request.form.get("status")
        if new_status not in ("pending", "selected", "waitlisted", "rejected", "cancelled"):
            flash("Invalid registration status.", "danger")
            return redirect(url_for("auth.participants", event_id=event_id))

        db = Database()
        registration = db.fetch_one("""
            SELECT r.*, e.title, e.organizer_id
            FROM registrations r
            JOIN events e ON r.event_id=e.id
            WHERE r.id=%s AND r.event_id=%s AND e.organizer_id=%s
        """, (registration_id, event_id, session["user_id"]))
        if not registration:
            db.close()
            flash("Registration not found.", "danger")
            return redirect(url_for("auth.participants", event_id=event_id))

        db.execute(
            "UPDATE registrations SET status=%s, attended=FALSE, certificate_available=FALSE WHERE id=%s",
            (new_status, registration_id),
        )
        db.close()
        notify_user(registration["student_id"], f"Your registration for {registration['title']} is now {new_status}.")
        if registration["status"] == "selected" and new_status != "selected":
            promote_waitlisted_student(event_id, registration["title"])
        flash("Registration status updated.", "success")
        return redirect(url_for("auth.participants", event_id=event_id))

    @login_required
    @role_required("organizer")
    def update_event_status(self, event_id):
        event_status = request.form.get("event_status")
        if event_status not in ("upcoming", "ongoing", "completed", "cancelled"):
            flash("Invalid event status.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))
        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND organizer_id=%s",
            (event_id, session["user_id"]))
        if not event:
            db.close()
            flash("Event not found or access denied.", "danger")
            return redirect(url_for("auth.organizer_dashboard"))
        db.execute("UPDATE events SET event_status=%s WHERE id=%s", (event_status, event_id))
        db.close()
        flash("Event status updated.", "success")
        return redirect(url_for("auth.organizer_dashboard"))
