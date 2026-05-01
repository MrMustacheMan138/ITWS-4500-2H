"""
Integration tests for /api/v1/auth endpoints.

Uses the FastAPI test client with an in-memory SQLite DB.
"""

import pytest
import pytest_asyncio


pytestmark = pytest.mark.asyncio


class TestSignup:
    async def test_signup_success(self, client, db):
        resp = await client.post("/api/v1/auth/signup", json={
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "name": "New User",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "created_at" in data
        # Password must NOT be returned
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_signup_normalises_email_to_lowercase(self, client, db):
        resp = await client.post("/api/v1/auth/signup", json={
            "email": "UPPER@Example.COM",
            "password": "SecurePass123",
            "name": "Upper User",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "upper@example.com"

    async def test_signup_duplicate_email_returns_400(self, client, db):
        payload = {"email": "dup@example.com", "password": "Pass123", "name": "Dup"}
        await client.post("/api/v1/auth/signup", json=payload)
        resp = await client.post("/api/v1/auth/signup", json=payload)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    async def test_signup_invalid_email_returns_422(self, client, db):
        resp = await client.post("/api/v1/auth/signup", json={
            "email": "not-an-email",
            "password": "Pass123",
            "name": "Bad Email",
        })
        assert resp.status_code == 422

    async def test_signup_password_too_long_returns_400(self, client, db):
        resp = await client.post("/api/v1/auth/signup", json={
            "email": "longpass@example.com",
            "password": "x" * 73,
            "name": "Long Pass",
        })
        assert resp.status_code == 400
        assert "72" in resp.json()["detail"]

    async def test_signup_password_at_limit_is_accepted(self, client, db):
        resp = await client.post("/api/v1/auth/signup", json={
            "email": "limit@example.com",
            "password": "x" * 72,
            "name": "Limit",
        })
        assert resp.status_code == 200

    async def test_signup_missing_name_returns_422(self, client, db):
        resp = await client.post("/api/v1/auth/signup", json={
            "email": "noname@example.com",
            "password": "Pass123",
        })
        assert resp.status_code == 422


class TestLogin:
    async def _create_user(self, client, db, email="login@example.com", password="Correct123"):
        await client.post("/api/v1/auth/signup", json={
            "email": email,
            "password": password,
            "name": "Login User",
        })

    async def test_login_success_returns_token(self, client, db):
        await self._create_user(client, db)
        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "Correct123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "login@example.com"

    async def test_login_wrong_password_returns_401(self, client, db):
        await self._create_user(client, db)
        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "WrongPassword",
        })
        assert resp.status_code == 401

    async def test_login_unknown_email_returns_401(self, client, db):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "ghost@example.com",
            "password": "AnyPassword",
        })
        assert resp.status_code == 401

    async def test_login_email_case_insensitive(self, client, db):
        await self._create_user(client, db, email="case@example.com")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "CASE@EXAMPLE.COM",
            "password": "Correct123",
        })
        assert resp.status_code == 200

    async def test_login_returns_is_admin_field(self, client, db):
        await self._create_user(client, db)
        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "Correct123",
        })
        assert "is_admin" in resp.json()

    async def test_login_invalid_email_format_returns_422(self, client, db):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "bad-email",
            "password": "Pass123",
        })
        assert resp.status_code == 422