from flask import render_template, request

class AuthController:

    def login(self):
        if request.method == "POST":
            print(request.form)
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
