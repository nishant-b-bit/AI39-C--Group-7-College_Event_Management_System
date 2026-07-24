
import unittest

from flask import Blueprint, Flask, session

from app.controllers.helpers import login_required, role_required


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    bp = Blueprint("auth", __name__)

    @bp.route("/login")
    def login():
        return "login page"

    @bp.route("/")
    def home():
        return "home page"

    @bp.route("/student")
    @login_required
    def student():
        return "student page"

    @bp.route("/admin")
    @role_required("admin")
    def admin():
        return "admin page"

    app.register_blueprint(bp)
    return app


class TestLoginRequired(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.client = self.app.test_client()

    def test_locked_page_redirects_guest_to_login(self):
        response = self.client.get("/student")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_locked_page_opens_for_logged_in_user(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        response = self.client.get("/student")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "student page")


class TestRoleRequired(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.client = self.app.test_client()

    def test_role_page_redirects_guest_to_login(self):
        response = self.client.get("/admin")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_role_page_rejects_wrong_role(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "student"

        response = self.client.get("/admin")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/"))

    def test_role_page_opens_for_allowed_role(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "admin"

        response = self.client.get("/admin")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "admin page")


if __name__ == "__main__":
    unittest.main()
