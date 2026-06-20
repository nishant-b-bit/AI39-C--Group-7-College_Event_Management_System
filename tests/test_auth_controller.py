"""
    python -m pytest tests/test_auth_controller.py -v
"""

import unittest
from unittest.mock import MagicMock, patch

from flask import Blueprint, Flask, get_flashed_messages, session

from app.controllers.auth import AuthController
from app.controllers.helpers import hash_password


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    bp = Blueprint("auth", __name__)
    bp.route("/login", endpoint="login")(lambda: "login")
    bp.route("/student_dashboard", endpoint="student_dashboard")(lambda: "student")
    bp.route("/organizer_dashboard", endpoint="organizer_dashboard")(lambda: "organizer")
    bp.route("/admin_dashboard", endpoint="admin_dashboard")(lambda: "admin")
    app.register_blueprint(bp)
    return app


class TestRegister(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.render_template")
    def test_register_get_shows_signup_form(self, mock_render):
        mock_render.return_value = "signup_page"

        with self.app.test_request_context(method="GET"):
            result = self.controller.register()

        self.assertEqual(result, "signup_page")
        mock_render.assert_called_once_with("signup.html")

    @patch("app.controllers.auth.render_template")
    def test_register_missing_fields_is_rejected(self, mock_render):
        mock_render.return_value = "signup_page"

        with self.app.test_request_context(
            method="POST",
            data={"name": "", "email": "", "password": ""},
        ):
            result = self.controller.register()
            flashes = get_flashed_messages(with_categories=True)

        self.assertEqual(result, "signup_page")
        self.assertIn(("danger", "All fields are required."), flashes)

    @patch("app.controllers.auth.render_template")
    def test_register_short_password_is_rejected(self, mock_render):
        mock_render.return_value = "signup_page"

        with self.app.test_request_context(
            method="POST",
            data={"name": "Asha", "email": "asha@example.com", "password": "123"},
        ):
            result = self.controller.register()
            flashes = get_flashed_messages(with_categories=True)

        self.assertEqual(result, "signup_page")
        self.assertIn(("danger", "Password must be at least 6 characters."), flashes)

    @patch("app.controllers.auth.Database")
    @patch("app.controllers.auth.render_template")
    def test_register_duplicate_email_is_rejected(self, mock_render, mock_db_class):
        mock_render.return_value = "signup_page"
        fake_db = MagicMock()
        fake_db.fetch_one.return_value = {"id": 1}
        mock_db_class.return_value = fake_db

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Asha",
                "email": "taken@example.com",
                "password": "secret1",
                "role": "student",
            },
        ):
            result = self.controller.register()
            flashes = get_flashed_messages(with_categories=True)

        self.assertEqual(result, "signup_page")
        self.assertIn(("danger", "An account with that email already exists."), flashes)
        fake_db.execute.assert_not_called()
        fake_db.close.assert_called_once()

    @patch("app.controllers.auth.Database")
    def test_register_success_saves_user_and_redirects(self, mock_db_class):
        fake_db = MagicMock()
        fake_db.fetch_one.return_value = None
        mock_db_class.return_value = fake_db

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Asha",
                "email": "asha@example.com",
                "password": "secret1",
                "role": "organizer",
            },
        ):
            response = self.controller.register()
            flashes = get_flashed_messages(with_categories=True)

        fake_db.execute.assert_called_once()
        saved_params = fake_db.execute.call_args.args[1]
        self.assertEqual(saved_params[0], "Asha")
        self.assertEqual(saved_params[1], "asha@example.com")
        self.assertEqual(saved_params[2], hash_password("secret1"))
        self.assertEqual(saved_params[3], "organizer")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        self.assertIn(("success", "Account created! Please log in."), flashes)


class TestHome(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.render_template")
    def test_home_shows_for_guest(self, mock_render):
        mock_render.return_value = "home_page"

        with self.app.test_request_context(method="GET"):
            result = self.controller.home()

        self.assertEqual(result, "home_page")
        mock_render.assert_called_once_with("home.html")

    def test_home_redirects_logged_in_student_to_dashboard(self):
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 2
            session["role"] = "student"

            response = self.controller.home()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/student_dashboard", response.location)

    def test_home_redirects_logged_in_organizer_to_dashboard(self):
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 3
            session["role"] = "organizer"

            response = self.controller.home()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/organizer_dashboard", response.location)

    def test_home_redirects_logged_in_admin_to_dashboard(self):
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 4
            session["role"] = "admin"

            response = self.controller.home()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin_dashboard", response.location)


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.render_template")
    def test_login_get_shows_login_form(self, mock_render):
        mock_render.return_value = "login_page"

        with self.app.test_request_context(method="GET"):
            result = self.controller.login()

        self.assertEqual(result, "login_page")
        mock_render.assert_called_once_with("login.html")

    @patch("app.controllers.auth.render_template")
    def test_login_missing_fields_is_rejected(self, mock_render):
        mock_render.return_value = "login_page"

        with self.app.test_request_context(
            method="POST",
            data={"email": "", "password": ""},
        ):
            result = self.controller.login()
            flashes = get_flashed_messages(with_categories=True)

        self.assertEqual(result, "login_page")
        self.assertIn(("danger", "Email and password are required."), flashes)

    @patch("app.controllers.auth.Database")
    @patch("app.controllers.auth.render_template")
    def test_login_wrong_password_is_rejected(self, mock_render, mock_db_class):
        mock_render.return_value = "login_page"
        fake_db = MagicMock()
        fake_db.fetch_one.return_value = None
        mock_db_class.return_value = fake_db

        with self.app.test_request_context(
            method="POST",
            data={"email": "asha@example.com", "password": "wrongpass"},
        ):
            result = self.controller.login()
            flashes = get_flashed_messages(with_categories=True)
            self.assertNotIn("user_id", session)

        self.assertEqual(result, "login_page")
        self.assertIn(("danger", "Invalid email or password."), flashes)
        fake_db.close.assert_called_once()

    @patch("app.controllers.auth.Database")
    def test_login_success_sets_session_and_redirects_student(self, mock_db_class):
        fake_db = MagicMock()
        fake_db.fetch_one.return_value = {
            "id": 2,
            "name": "Asha",
            "email": "asha@example.com",
            "password": hash_password("secret1"),
            "role": "student",
        }
        mock_db_class.return_value = fake_db

        with self.app.test_request_context(
            method="POST",
            data={"email": "asha@example.com", "password": "secret1"},
        ):
            response = self.controller.login()
            self.assertEqual(session["user_id"], 2)
            self.assertEqual(session["name"], "Asha")
            self.assertEqual(session["role"], "student")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/student_dashboard", response.location)
        fake_db.close.assert_called_once()


class TestLogout(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_logout_clears_session_and_redirects_to_login(self):
        with self.app.test_request_context():
            session["user_id"] = 9
            session["name"] = "Asha"
            session["role"] = "student"

            response = self.controller.logout()
            flashes = get_flashed_messages(with_categories=True)
            self.assertNotIn("user_id", session)
            self.assertNotIn("name", session)
            self.assertNotIn("role", session)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        self.assertIn(("success", "You have been logged out."), flashes)


if __name__ == "__main__":
    unittest.main()
