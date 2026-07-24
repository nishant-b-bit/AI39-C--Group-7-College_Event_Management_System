
import unittest
from unittest.mock import patch

from app import create_app
from app.routes import create_auth_blueprint


class TestFlaskBasics(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.register_blueprint(create_auth_blueprint())
        self.client = self.app.test_client()

    def test_home_page_is_public(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Eventix", response.data.decode())

    def test_login_page_is_public(self):
        response = self.client.get("/login")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Login", response.data.decode())

    def test_student_dashboard_redirects_guest_to_login(self):
        response = self.client.get("/student_dashboard")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    @patch("app.controllers.auth.Database")
    def test_login_with_valid_student_redirects_to_dashboard(self, mock_db_class):
        fake_db = mock_db_class.return_value
        fake_db.fetch_one.return_value = {
            "id": 3,
            "name": "Asha",
            "email": "asha@example.com",
            "password": "secret1",
            "role": "student",
        }

        response = self.client.post(
            "/login",
            data={"email": "asha@example.com", "password": "secret1"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/student_dashboard", response.location)


if __name__ == "__main__":
    unittest.main()
