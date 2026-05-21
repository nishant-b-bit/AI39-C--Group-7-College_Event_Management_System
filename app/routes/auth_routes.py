from flask import Blueprint
from app.controllers.auth import AuthController
class AuthRoutes:
    def __init__(self):
        self.bp=Blueprint("auth",__name__)
        self.controller=AuthController()
    def register(self):
        self.bp.route("/login",methods=["GET","POST"])(self.controller.login)
        self.bp.route("/register",methods=["GET","POST"])(self.controller.register)
        self.bp.route("/base",methods=["GET","POST"])(self.controller.base)
        self.bp.route("/contact",methods=["GET","POST"])(self.controller.contact)
        self.bp.route("/about",methods=["GET","POST"])(self.controller.about)
        self.bp.route("/",methods=["GET","POST"])(self.controller.home)

        return self.bp