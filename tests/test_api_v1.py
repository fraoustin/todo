# test_api_v1.py
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

    def test_version(self):
        response = self.client.get("/api/v1/version")
        self.assertEqual(response.status_code, 200)
        self.assertIn("version", response.json())

    def test_no_access(self):
        response = self.client.post("/api/v1/todo", content='{}')
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/v1/todos")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/v1/todo/1")
        self.assertEqual(response.status_code, 401)
        response = self.client.put("/api/v1/todo/1", content='{}')
        self.assertEqual(response.status_code, 401)
        response = self.client.delete("/api/v1/todo/1")
        self.assertEqual(response.status_code, 401)

    def test_create_todo(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/v1/todo", headers=headers, content='{"text": "first todo", "terminated": false}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("first todo", response.json()["text"])

    def test_get_todo(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/v1/todo", headers=headers, content='{"text": "first todo", "terminated": false}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("first todo", response.json()["text"])
        id = response.json()["id"]
        response = self.client.get(f"/api/v1/todo/{id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("first todo", response.json()["text"])

    def test_update_todo(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/v1/todo", headers=headers, content='{"text": "first todo", "terminated": false}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("first todo", response.json()["text"])
        id = response.json()["id"]
        response = self.client.get(f"/api/v1/todo/{id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("first todo", response.json()["text"])
        self.client.put(f"/api/v1/todo/{id}", headers=headers, content='{"text": "firsttt todo"}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"/api/v1/todo/{id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("firsttt todo", response.json()["text"])
        self.client.put(f"/api/v1/todo/{id}", headers=headers, content='{"terminated": true}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"/api/v1/todo/{id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(True, response.json()["terminated"])

    def test_todos(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/v1/todos", headers=headers)
        self.assertEqual(response.status_code, 200)
        cnt = len(response.json())
        response = self.client.post("/api/v1/todo", headers=headers, content='{"text": "second todo", "terminated": false}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/v1/todos", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cnt+1, len(response.json()))

    def test_delete_todo(self):
        token_response = self.client.post("/api/token", data={"username": "admin", "password": "secret"})
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/v1/todos", headers=headers)
        self.assertEqual(response.status_code, 200)
        cnt = len(response.json())
        response = self.client.post("/api/v1/todo", headers=headers, content='{"text": "other todo", "terminated": false}')
        self.assertEqual(response.status_code, 200)
        id = response.json()["id"]
        response = self.client.get("/api/v1/todos", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cnt+1, len(response.json()))
        self.client.delete(f"/api/v1/todo/{id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/v1/todos", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cnt, len(response.json()))