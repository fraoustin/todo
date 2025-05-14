# test_auth.py
import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
os.environ["ENV"] = "unittest"

from main import app
from db import cleanDb


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
    
    @classmethod
    def tearDownClass(cls):
        cleanDb()

    def test_token_success(self):
        response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_token_failure(self):
        response = self.client.post("/api/token", data={"username": "admin", "password": "wrong"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "User or password invalid")

    def test_protected_route_with_token(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("admin", response.json()["username"])

    def test_protected_route_invalid_token(self):
        headers = {"Authorization": "Bearer fake-token"}
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Token invalid")

    def test_create_user(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/user", headers=headers, content='{"username": "test", "email": "test@example.com", "disabled": false,  "isadmin": false, "onlyapi": false, "password": "123456"}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("test", response.json()["username"])
        token_response = self.client.post("/api/token", data={"username": "test", "password": "123456"})
        self.assertTrue(len(token_response.json().get("access_token", "")) > 0)

    def test_not_admin(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/user", headers=headers, content='{"username": "test", "email": "test@example.com", "disabled": false,  "isadmin": false, "onlyapi": false, "password": "123456"}')
        token_response = self.client.post("/api/token", data={"username": "test", "password": "123456"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/user", headers=headers, content='{"username": "test2", "email": "test2@example.com", "disabled": false,  "isadmin": false, "onlyapi": false, "password": "123456"}')
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/user/99", headers=headers)
        self.assertEqual(response.status_code, 401)
        response = self.client.delete("/api/user/99", headers=headers)
        self.assertEqual(response.status_code, 401)
        response = self.client.put("/api/user/99", headers=headers, content='{"email": "testchange@example.com"}')
        self.assertEqual(response.status_code, 401)

    def test_me(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("admin@example.com", response.json()["email"])

    def test_update_me(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("admin@example.com", response.json()["email"])
        response = self.client.put("/api/me", headers=headers, content='{"email": "testchange@example.com"}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("testchange@example.com", response.json()["email"])
        response = self.client.put("/api/me", headers=headers, content='{"isadmin": true}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(True, response.json()["isadmin"])
        response = self.client.put("/api/me", headers=headers, content='{"isadmin": false}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_users(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/users", headers=headers)
        self.assertEqual(response.status_code, 200)
        lenusers = len(response.json())
        response = self.client.post("/api/user", headers=headers, content='{"username": "test3", "email": "test3@example.com", "disabled": false,  "isadmin": false, "onlyapi": false, "password": "123456"}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/users", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), lenusers+1)

    def test_delete_user(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/users", headers=headers)
        self.assertEqual(response.status_code, 200)
        lenusers = len(response.json())
        response = self.client.post("/api/user", headers=headers, content='{"username": "test4", "email": "test4@example.com", "disabled": false,  "isadmin": false, "onlyapi": false, "password": "123456"}')
        self.assertEqual(response.status_code, 200)
        newid = response.json()["id"]
        response = self.client.delete(f"/api/user/{newid}", headers=headers)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/users", headers=headers)
        self.assertEqual(len(response.json()), lenusers)

    def test_get_user(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/me", headers=headers)
        newid = response.json()["id"]
        response = self.client.get(f"/api/user/{newid}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], "admin")
        response = self.client.get("/api/user/99", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/users", headers=headers)
        self.assertEqual(response.status_code, 200)
        lenusers = len(response.json())
        response = self.client.post("/api/user", headers=headers, content='{"username": "test5", "email": "test5@example.com", "disabled": false,  "isadmin": false, "onlyapi": false, "password": "123456"}')
        self.assertEqual(response.status_code, 200)
        newid = response.json()["id"]
        response = self.client.get(f"/api/user/{newid}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], "test5@example.com")
        response = self.client.put(f"/api/user/{newid}", headers=headers, content='{"email": "test5change@example.com"}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"/api/user/{newid}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], "test5change@example.com")

    def test_disabled(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/user", headers=headers, content='{"username": "test6", "email": "test6@example.com", "disabled": false,  "isadmin": false, "onlyapi": false, "password": "123456"}')
        self.assertEqual(response.status_code, 200)
        token_response = self.client.post("/api/token", data={"username": "test6", "password": "123456"})
        self.assertEqual(response.status_code, 200)
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.put("/api/me", headers=headers, content='{"disabled": "true"}')
        self.assertEqual(response.status_code, 200)
        token_response = self.client.post("/api/token", data={"username": "test6", "password": "123456"})
        self.assertEqual(token_response.status_code, 400)


if __name__ == "__main__":
    unittest.main()