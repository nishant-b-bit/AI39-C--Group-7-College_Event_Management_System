from datetime import date

from flask import Response, flash, redirect, render_template, request, session, url_for

from app.controllers.helpers import (
    login_required,
    notify_user,
    promote_waitlisted_student,
    role_required,
)
from app.models.database import Database


class StudentController:
    @login_required
    @role_required("student")
    def student_dashboard(self):
        db = Database()
        my_registrations = db.fetch_all("""
            SELECT e.id, e.title, e.date, e.location, e.event_status, e.status AS approval_status,
                   r.id AS registration_id, r.attended, r.status AS registration_status,
                   r.certificate_available
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            WHERE r.student_id = %s
            ORDER BY e.date DESC
        """, (session["user_id"],))

        available_events = db.fetch_all("""
            SELECT e.id, e.title, e.date, e.location, e.genre,
                   e.capacity, e.event_status,
                   (SELECT COUNT(*) FROM registrations WHERE event_id = e.id AND status='selected') AS registered
            FROM events e
            WHERE e.status = 'approved'
              AND e.event_status IN ('upcoming', 'ongoing')
              AND e.id NOT IN (
                  SELECT event_id FROM registrations
                  WHERE student_id = %s AND status != 'cancelled'
              )
            ORDER BY e.date ASC
        """, (session["user_id"],))

        stats = {
            "registered_events": len(my_registrations),
            "upcoming": sum(1 for r in my_registrations if r["date"] >= date.today() and not r["attended"]),
            "completed": sum(1 for r in my_registrations if r["event_status"] == "completed" or r["attended"]),
            "waitlisted": sum(1 for r in my_registrations if r["registration_status"] == "waitlisted"),
        }
        db.close()
        return render_template(
            "student_dashboard.html",
            my_registrations=my_registrations,
            available_events=available_events,
            stats=stats,
        )

    @login_required
    @role_required("student")
    def register_for_event(self):
        event_id = request.form.get("event_id")
        if not event_id:
            flash("Invalid event.", "danger")
            return redirect(url_for("auth.student_dashboard"))

        db = Database()
        event = db.fetch_one(
            "SELECT * FROM events WHERE id=%s AND status='approved' AND event_status IN ('upcoming', 'ongoing')",
            (event_id,),
        )
        if not event:
            db.close()
            flash("Event not found or not approved.", "danger")
            return redirect(url_for("auth.student_dashboard"))

        existing = db.fetch_one(
            "SELECT id, status FROM registrations WHERE event_id=%s AND student_id=%s",
            (event_id, session["user_id"]))
        if existing and existing["status"] != "cancelled":
            db.close()
            flash("You are already registered for this event.", "warning")
            return redirect(url_for("auth.student_dashboard"))

        selected_count = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM registrations WHERE event_id=%s AND status='selected'",
            (event_id,),
        )["cnt"]
        registration_status = "selected" if selected_count < event["capacity"] else "waitlisted"

        if existing:
            db.execute(
                "UPDATE registrations SET status=%s, attended=FALSE, certificate_available=FALSE WHERE id=%s",
                (registration_status, existing["id"]),
            )
        else:
            db.execute(
                "INSERT INTO registrations (event_id, student_id, status) VALUES (%s, %s, %s)",
                (event_id, session["user_id"], registration_status))
        db.close()
        if registration_status == "waitlisted":
            notify_user(session["user_id"], f"You were added to the waitlist for {event['title']}.")
            flash("Event is full. You have been added to the waitlist.", "warning")
        else:
            notify_user(session["user_id"], f"Registration successful for {event['title']}.")
            flash("Successfully registered for the event!", "success")
        return redirect(url_for("auth.student_dashboard"))

    @login_required
    @role_required("student")
    def cancel_registration(self, registration_id):
        db = Database()
        registration = db.fetch_one("""
            SELECT r.*, e.title
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            WHERE r.id=%s AND r.student_id=%s
        """, (registration_id, session["user_id"]))
        if not registration:
            db.close()
            flash("Registration not found.", "danger")
            return redirect(url_for("auth.student_dashboard"))

        db.execute(
            "UPDATE registrations SET status='cancelled', attended=FALSE, certificate_available=FALSE WHERE id=%s",
            (registration_id,),
        )
        db.close()
        if registration["status"] == "selected":
            promote_waitlisted_student(registration["event_id"], registration["title"])
        flash("Registration cancelled.", "success")
        return redirect(url_for("auth.student_dashboard"))

    @login_required
    @role_required("student")
    def download_certificate(self, registration_id):
        db = Database()
        registration = db.fetch_one("""
            SELECT r.*, e.title, e.date, u.name
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            JOIN users u ON r.student_id = u.id
            WHERE r.id=%s AND r.student_id=%s
        """, (registration_id, session["user_id"]))
        db.close()
        if not registration or not registration["certificate_available"]:
            flash("Certificate is not available yet.", "danger")
            return redirect(url_for("auth.student_dashboard"))

        content = (
            "Certificate of Participation\n\n"
            f"This certifies that {registration['name']} participated in {registration['title']} "
            f"on {registration['date']}.\n"
        )
        return Response(
            content,
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment; filename=certificate-{registration_id}.txt"},
        )
