import unittest

from service import create_app
from service.models import db


class AccountsApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "FORCE_HTTPS": False,
            }
        )
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_account(self, email="alex@example.com"):
        return self.client.post(
            "/accounts",
            json={
                "name": "Alex Customer",
                "email": email,
                "phone": "555-0100",
                "account_type": "personal",
                "balance": 25.5,
            },
        )

    def test_create_and_read_account(self):
        response = self.create_account()
        self.assertEqual(response.status_code, 201)
        account_id = response.get_json()["id"]

        read_response = self.client.get(f"/accounts/{account_id}")
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.get_json()["email"], "alex@example.com")

    def test_home_page_returns_service_name_and_version(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"name": "Account REST API Service", "version": "1.0"},
        )

    def test_list_accounts(self):
        self.create_account()
        response = self.client.get("/accounts")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["count"], 1)
        self.assertEqual(len(response.get_json()["accounts"]), 1)

    def test_update_account(self):
        account_id = self.create_account().get_json()["id"]
        response = self.client.put(
            f"/accounts/{account_id}",
            json={"name": "Alex Updated", "balance": 40},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Alex Updated")
        self.assertEqual(response.get_json()["balance"], 40.0)

    def test_delete_account(self):
        account_id = self.create_account().get_json()["id"]
        response = self.client.delete(f"/accounts/{account_id}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["deleted"])
        self.assertEqual(self.client.get(f"/accounts/{account_id}").status_code, 404)

    def test_delete_account_by_email_returns_no_content(self):
        self.create_account()
        response = self.client.delete("/accounts", json={"email": "alex@example.com"})

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_data(), b"")
        self.assertEqual(self.client.get("/accounts/1").status_code, 404)

    def test_create_requires_name_and_email(self):
        response = self.client.post("/accounts", json={"name": "Alex"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("email is required", response.get_json()["error"])

    def test_duplicate_email_is_rejected(self):
        self.create_account()
        response = self.create_account()

        self.assertEqual(response.status_code, 409)

    def test_missing_account_returns_json_404(self):
        response = self.client.get("/accounts/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Account not found"})

    def test_invalid_balance_is_rejected(self):
        response = self.client.post(
            "/accounts",
            json={"name": "Alex", "email": "alex@example.com", "balance": -1},
        )

        self.assertEqual(response.status_code, 400)

    def test_cors_preflight_and_security_headers(self):
        response = self.client.options(
            "/accounts",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")


if __name__ == "__main__":
    unittest.main()
