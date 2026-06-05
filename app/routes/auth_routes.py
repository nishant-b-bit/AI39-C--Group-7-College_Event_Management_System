from flask import Blueprint
from app.controllers.auth import AuthController
class AuthRoutes:
    def __init__(self):
        self.bp=Blueprint("auth",__name__)
        self.controller=AuthController()
    def register(self):
        self.bp.route("/login",methods=["GET","POST"])(self.controller.login)
        self.bp.route("/signup", methods=["GET", "POST"])(self.controller.register)
        self.bp.route("/base",methods=["GET","POST"])(self.controller.base)
        self.bp.route("/contact",methods=["GET","POST"])(self.controller.contact)
        self.bp.route("/about",methods=["GET","POST"])(self.controller.about)
        self.bp.route("/",methods=["GET","POST"])(self.controller.home)
        self.bp.route("/event_details",methods=["GET","POST"])(self.controller.eventdetails)
        self.bp.route("/create_events",methods=["GET","POST"])(self.controller.create_events)
        self.bp.route("/organizer_dashboard", methods=["GET", "POST"])(self.controller.organizer_dashboard)
        self.bp.route("/register_event", methods=["GET", "POST"])(self.controller.register_event)
        self.bp.route("/view_events", methods=["GET", "POST"])(self.controller.view_events)
        self.bp.route("/student_dashboard")(self.controller.student_dashboard)
        self.bp.route("/admin_dashboard")(self.controller.admin_dashboard) 
        self.bp.route("/edit_event",methods=["GET","POST"])(self.controller.edit_event)
        return self.bp