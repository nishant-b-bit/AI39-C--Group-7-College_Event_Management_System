from flask import render_template, request, redirect, url_for
from app.models.user_model import User

class AuthController:

    def login(self):
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = User.login_user(email, password)

            if user:
                if user["role"] == "student":
                    return redirect(url_for("student.dashboard"))

                elif user["role"] == "organizer":
                    return redirect(url_for("organizer.dashboard"))

                elif user["role"] == "admin":
                    return redirect(url_for("admin.dashboard"))

            return "Invalid Credentials"

        return render_template("login.html")

    def signup(self):
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            role = request.form.get("role")

            User.create_user(name, email, password, role)

            return "User registered successfully"

        return render_template("signup.html")