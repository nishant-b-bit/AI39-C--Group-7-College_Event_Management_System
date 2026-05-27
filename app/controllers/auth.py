from flask import render_template, request,redirect, url_for
class AuthController:
 
    def login(self):
     return render_template("login.html")
 
    def register(self):
        if request.method == "POST":
            print(request.form)
        return render_template("register.html")
 
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
 
    def signup(self):
        return render_template("signup.html")
 
    def view_events(self):
 
        # temporary dummy data (later we will fetch from DB)
        events = [
            {
                "title": "Tech Summit 2026",
                "genre": "Technical",
                "date": "2026-05-15",
                "location": "Main Auditorium"
            },
            {
                "title": "Music Fest Night",
                "genre": "Entertainment",
                "date": "2026-06-10",
                "location": "City Hall"
            },
            {
                "title": "AI Workshop",
                "genre": "Technical",
                "date": "2026-05-30",
                "location": "Lab 3"
            }
        ]
 
        return render_template("view_events.html", events=events)