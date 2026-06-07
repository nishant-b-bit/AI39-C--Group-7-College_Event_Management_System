from flask import Blueprint

from app.controllers.admin import AdminController
from app.controllers.auth import AuthController
from app.controllers.organizer import OrganizerController
from app.controllers.student import StudentController
from app.routes.admin_routes import register_admin_routes
from app.routes.organizer_routes import register_organizer_routes
from app.routes.public_routes import (
    register_auth_routes,
    register_event_routes,
    register_public_routes,
)
from app.routes.student_routes import register_student_routes


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.auth_controller = AuthController()
        self.student_controller = StudentController()
        self.organizer_controller = OrganizerController()
        self.admin_controller = AdminController()

    def register(self):
        auth = self.auth_controller
        student = self.student_controller
        organizer = self.organizer_controller
        admin = self.admin_controller

        register_public_routes(self.bp, auth)
        register_auth_routes(self.bp, auth)
        register_event_routes(self.bp, auth)
        register_student_routes(self.bp, student)
        register_organizer_routes(self.bp, organizer)
        register_admin_routes(self.bp, admin)

        return self.bp
