from flask import render_template

from flask import Blueprint 

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    return render_template("home.html")

@home_bp.route("/login")
def login():
    return render_template("login.html")

@home_bp.route("/register")
def register():
    return render_template("register.html")

@home_bp.route("/event_details")
def eventdetail():
    return render_template("event_details.html")

@home_bp.route("/signup")
def signup():
    return render_template("signup.html")