from flask import render_template, request,redirect, url_for
from app.models.database import Database
class AuthController:
 
    def login(self):
        if request.method=="POST":
            print(request.form)
        return render_template("login.html")
    
    def register(self):
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            role = request.form.get("role")
            
            db= Database()
            db.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, password, role)
            )

            return redirect(url_for("auth.login"))
        return render_template("signup.html")
 
    def base(self):
        return render_template("base.html")
 
    def contact(self):
        return render_template("contact.html")
 
    def about(self):
        return render_template("about.html")
 
    def home(self):
        return render_template("home.html")
 
    def eventdetails(self):
        return render_template("event_details.html")
 
 
    def create_events(self):
        return render_template("create_events.html")
    
    def view_events(self):

     events = [
        {
            "id": 1,
            "title": "Tech Summit 2026",
            "genre": "Technical",
            "date": "2026-05-15",
            "location": "Main Auditorium",
            "description": "Join Nepal's biggest technology summit with workshops and networking.",
            "image": "event1.jpg"
        },
        {
            "id": 2,
            "title": "Music Fest Night",
            "genre": "Entertainment",
            "date": "2026-06-10",
            "location": "City Hall",
            "description": "A night full of live music, fun, and performances.",
            "image": "event2.jpg"
        },
        {
            "id": 3,
            "title": "AI Workshop",
            "genre": "Technical",
            "date": "2026-05-30",
            "location": "Lab 3",
            "description": "Hands-on AI workshop for students and developers.",
            "image": "event3.jpg"
        }
    ]

     return render_template(
        "view_events.html",
        events=events
    )
    
    def organizer_dashboard(self):

    # Dummy event data
        events = [
        {
            "id": 1,
            "title": "Tech Summit 2026",
            "date": "2026-05-15",
            "status": "Approved",
            "registrations": 145,
            "capacity": 200,
            "approvalStatus": "approved",
        },
        {
            "id": 2,
            "title": "Workshop on AI",
            "date": "2026-05-20",
            "status": "Pending",
            "registrations": 0,
            "capacity": 50,
            "approvalStatus": "pending",
        },
        {
            "id": 3,
            "title": "Cultural Fest",
            "date": "2026-04-20",
            "status": "Ended",
            "registrations": 320,
            "capacity": 500,
            "approvalStatus": "approved",
        }
    ]

    # Dashboard statistics
        stats = {
        "total_events": len(events),
        "active_events": 2,
        "total_registrations": 465,
        "pending_approval": 1
    }

        return render_template(
        "organizer_dashboard.html",
        events=events,
        stats=stats
    )
    def register_event(self):

     event = {
        "title": "Tech Summit 2026",
        "date": "2026-05-15",
        "time": "10:00 AM",
        "venue": "Main Auditorium",
        "organizer": "Eventix Club",
        "description": "Join Nepal's biggest tech summit with workshops, networking, and innovation showcases."
    }

     return render_template(
        "register_event.html",
        event=event
    )