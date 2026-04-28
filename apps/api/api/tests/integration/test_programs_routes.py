"""
Integration tests for /api/v1/programs endpoints.
"""

import pytest

pytestmark = pytest.mark.asyncio


class TestCreateProgram:
    async def test_create_program_success(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.post("/api/v1/programs/", json={
            "name": "Computer Science",
            "description": "CS program",
            "institution": "MIT",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Computer Science"
        assert data["institution"] == "MIT"
        assert "id" in data

    async def test_create_program_without_auth_returns_401(self, client, db):
        resp = await client.post("/api/v1/programs/", json={"name": "Test"})
        assert resp.status_code == 401

    async def test_create_program_minimal_fields(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.post("/api/v1/programs/", json={"name": "Minimal"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Minimal"

    async def test_program_belongs_to_current_user(self, client, db, user_and_token):
        user, headers = user_and_token
        resp = await client.post("/api/v1/programs/", json={"name": "My Prog"}, headers=headers)
        assert resp.json()["user_id"] == user.id


class TestGetPrograms:
    async def test_get_programs_empty_list(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.get("/api/v1/programs/", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_programs_returns_own_programs(self, client, db, user_and_token):
        _, headers = user_and_token
        await client.post("/api/v1/programs/", json={"name": "Prog A"}, headers=headers)
        await client.post("/api/v1/programs/", json={"name": "Prog B"}, headers=headers)
        resp = await client.get("/api/v1/programs/", headers=headers)
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()]
        assert "Prog A" in names
        assert "Prog B" in names

    async def test_get_programs_without_auth_returns_401(self, client, db):
        resp = await client.get("/api/v1/programs/")
        assert resp.status_code == 401

    async def test_users_cannot_see_each_others_programs(self, client, db, user_and_token):
        from models import User
        from core.auth import get_password_hash, create_access_token

        _, headers_a = user_and_token

        # Create second user
        user_b = User(email="b@example.com", name="B", hashed_password=get_password_hash("pass"))
        db.add(user_b)
        await db.commit()
        await db.refresh(user_b)
        token_b = create_access_token({"sub": str(user_b.id)})
        headers_b = {"Authorization": f"Bearer {token_b}"}

        await client.post("/api/v1/programs/", json={"name": "User A Program"}, headers=headers_a)
        resp = await client.get("/api/v1/programs/", headers=headers_b)
        names = [p["name"] for p in resp.json()]
        assert "User A Program" not in names


class TestGetProgram:
    async def test_get_program_by_id(self, client, db, user_and_token):
        _, headers = user_and_token
        create_resp = await client.post("/api/v1/programs/", json={"name": "Specific"}, headers=headers)
        prog_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/programs/{prog_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Specific"

    async def test_get_nonexistent_program_returns_404(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.get("/api/v1/programs/99999", headers=headers)
        assert resp.status_code == 404

    async def test_get_other_users_program_returns_403(self, client, db, user_and_token):
        from models import User
        from core.auth import get_password_hash, create_access_token

        _, headers_a = user_and_token

        create_resp = await client.post("/api/v1/programs/", json={"name": "Private"}, headers=headers_a)
        prog_id = create_resp.json()["id"]

        user_b = User(email="b2@example.com", name="B2", hashed_password=get_password_hash("pass"))
        db.add(user_b)
        await db.commit()
        await db.refresh(user_b)
        token_b = create_access_token({"sub": str(user_b.id)})
        headers_b = {"Authorization": f"Bearer {token_b}"}

        resp = await client.get(f"/api/v1/programs/{prog_id}", headers=headers_b)
        assert resp.status_code == 403


class TestUpdateProgram:
    async def test_update_program_name(self, client, db, user_and_token):
        _, headers = user_and_token
        create_resp = await client.post("/api/v1/programs/", json={"name": "Old Name"}, headers=headers)
        prog_id = create_resp.json()["id"]
        resp = await client.put(f"/api/v1/programs/{prog_id}", json={"name": "New Name"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    async def test_partial_update_preserves_other_fields(self, client, db, user_and_token):
        _, headers = user_and_token
        create_resp = await client.post("/api/v1/programs/", json={
            "name": "CS", "institution": "MIT"
        }, headers=headers)
        prog_id = create_resp.json()["id"]
        resp = await client.put(f"/api/v1/programs/{prog_id}", json={"name": "CS Updated"}, headers=headers)
        assert resp.json()["institution"] == "MIT"

    async def test_update_nonexistent_program_returns_404(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.put("/api/v1/programs/99999", json={"name": "X"}, headers=headers)
        assert resp.status_code == 404


class TestDeleteProgram:
    async def test_delete_program_success(self, client, db, user_and_token):
        _, headers = user_and_token
        create_resp = await client.post("/api/v1/programs/", json={"name": "To Delete"}, headers=headers)
        prog_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/v1/programs/{prog_id}", headers=headers)
        assert resp.status_code == 204
        # Should be gone
        get_resp = await client.get(f"/api/v1/programs/{prog_id}", headers=headers)
        assert get_resp.status_code == 404

    async def test_delete_nonexistent_program_returns_404(self, client, db, user_and_token):
        _, headers = user_and_token
        resp = await client.delete("/api/v1/programs/99999", headers=headers)
        assert resp.status_code == 404

    async def test_delete_other_users_program_returns_403(self, client, db, user_and_token):
        from models import User
        from core.auth import get_password_hash, create_access_token

        _, headers_a = user_and_token
        create_resp = await client.post("/api/v1/programs/", json={"name": "Mine"}, headers=headers_a)
        prog_id = create_resp.json()["id"]

        user_b = User(email="b3@example.com", name="B3", hashed_password=get_password_hash("pass"))
        db.add(user_b)
        await db.commit()
        await db.refresh(user_b)
        headers_b = {"Authorization": f"Bearer {create_access_token({'sub': str(user_b.id)})}"}

        resp = await client.delete(f"/api/v1/programs/{prog_id}", headers=headers_b)
        assert resp.status_code == 403